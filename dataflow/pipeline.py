import argparse
from datetime import datetime

import apache_beam as beam
from apache_beam import ParDo
from apache_beam.options.pipeline_options import PipelineOptions
from dateutil.relativedelta import relativedelta

from custom.io_operations import (
    DeleteGCSFolderFn,
    ReadFromFirestore,
    ProcessTransaction,
    WriteUserFileFn,
)


def run(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--bucket", required=True, help="GCS bucket to write results to"
    )
    parser.add_argument("--date", required=True, help="Billing date")
    known_args, pipeline_args = parser.parse_known_args(argv)

    execution_date = datetime.strptime(known_args.date, "%Y-%m-%d")
    end_date = datetime(execution_date.year, execution_date.month, 1)
    start_date = end_date - relativedelta(months=1)
    # Filters for transactions collection
    transaction_filters = [
        ("date", ">=", start_date),
        ("date", "<", end_date),
        ("status", "==", "completed"),
    ]

    pipeline_options = PipelineOptions(pipeline_args)

    with beam.Pipeline(options=pipeline_options) as p:
        # Step 0: Delete existing files in the specified folder
        cleanup_pipeline = (
            p
            | "Start Pipeline" >> beam.Create([None])
            | "Delete Existing GCS Folder"
            >> ParDo(
                DeleteGCSFolderFn(
                    known_args.bucket,
                    f'{start_date.strftime("%Y")}/{start_date.strftime("%m")}/',
                )
            )
        )

        # Main pipeline starts after cleanup
        main_pipeline = cleanup_pipeline

        # Step 1: Read and process transactions, keyed by user_id
        transactions = (
            main_pipeline
            | "Read Transactions"
            >> ReadFromFirestore("transactions", transaction_filters)
            | "Map Transactions by User ID" >> ParDo(ProcessTransaction())
            | "Group by User ID" >> beam.GroupByKey()
            | "Calculate Total Fee" >> beam.Map(lambda x: (x[0], sum(x[1])))
        )

        # Step 2: Read counters collection, keyed by user_id
        counters = main_pipeline | "Read Counters" >> ReadFromFirestore(
            f'counters_{start_date.strftime("%Y")}_{start_date.strftime("%m")}'
        )

        # Step 3: Read users collection, keyed by user_id
        users = main_pipeline | "Read Users" >> ReadFromFirestore("users")

        # Step 4: Perform a join to ensure we keep all users, even those without transactions
        joined_data = (
            {"users": users, "transactions": transactions, "counters": counters}
            | "Join Users with Transactions and Counters" >> beam.CoGroupByKey()
            | "Merge Data"
            >> beam.Map(
                lambda x: (
                    x[0],
                    {
                        **(x[1]["users"][0] if x[1]["users"] else {}),
                        **(x[1]["counters"][0] if x[1]["counters"] else {}),
                        "total_fee": (
                            x[1]["transactions"][0] if x[1]["transactions"] else 0
                        ),
                    },
                )
            )
        )

        # Step 5: Write the joined data to GCS, partitioned by user_id
        joined_data | "Write User Files" >> ParDo(
            WriteUserFileFn(
                known_args.bucket,
                f'{start_date.strftime("%Y")}/{start_date.strftime("%m")}/',
            )
        )


if __name__ == "__main__":
    run()
