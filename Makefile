LOCATION = europe-west1
PROJECT = data-platform-exercise

.PHONY: create-docker-repo docker-build docker-publish docker-run template run-template \
		terraform-plan terraform-apply terraform-destroy populate-user-data populate-raw-transaction-data

create-docker-repo:
	@echo "Create Docker Repo"
	gcloud artifacts repositories create $(REPO_NAME) --repository-format=docker \
    --location=$(LOCATION) \
    --project=$(PROJECT)

docker-build:
	@echo "Build Docker in : $(DIR)"
	cd $(DIR) && docker build --platform linux/amd64 -t $(IMAGE_NAME) .

docker-publish:
	@echo "Publish Docker"
	docker tag cloud_run_service:latest $(LOCATION)-docker.pkg.dev/$(PROJECT)/$(REPO_NAME)/$(IMAGE_NAME) && docker push $(LOCATION)-docker.pkg.dev/$(PROJECT)/$(REPO_NAME)/$(IMAGE_NAME)

docker-run:
	@echo "Run Docker"
	docker run -it -p 8080:8080 -v "$(HOME)/.config/gcloud/application_default_credentials.json":/gcp/creds.json:ro --env GOOGLE_APPLICATION_CREDENTIALS=/gcp/creds.json --env GOOGLE_CLOUD_PROJECT=$(PROJECT) $(IMAGE_NAME)

template:
	gcloud dataflow flex-template build gs://billing-bucket-885070032799/templates/metadata.json \
	 --image-gcr-path $(LOCATION)-docker.pkg.dev/$(PROJECT)/monthly-billing-flow-repo/dataflow_pipeline:latest \
	 --sdk-language "PYTHON" \
	 --flex-template-base-image "gcr.io/dataflow-templates-base/python39-template-launcher-base" \
	 --metadata-file "dataflow/metadata.json" \
	 --py-path "dataflow/" \
	 --env "FLEX_TEMPLATE_PYTHON_PY_FILE=pipeline.py" \
	 --env "FLEX_TEMPLATE_PYTHON_SETUP_FILE=setup.py" \
	 --env "FLEX_TEMPLATE_PYTHON_REQUIREMENTS_FILE=requirements.txt"

run-template:
	gcloud dataflow flex-template run "monthly-billing-flow-`date +%Y%m%d-%H%M%S`" \
    --template-file-gcs-location "gs://billing-bucket-885070032799/templates/metadata.json" \
    --parameters bucket="billing-bucket-885070032799" \
    --parameters date="2024-10-01" \
    --region $(LOCATION)

terraform-plan:
	@echo "Planning deployment to directory: $(DIR)"
	cd $(DIR) && terraform plan

terraform-apply:
	@echo "Deploying to directory: $(DIR)"
	cd $(DIR) && terraform apply -auto-approve

terraform-destroy:
	cd $(DIR) && terraform apply -destroy

populate-user-data:
	python local/populator/firestore_initializer.py

populate-raw-transaction-data:
	python local/populator/raw_transaction_publisher.py

test_units_transaction_operations:
	# cd emulators && firebase emulators:start activate emulator
	export EVENT_MAX_AGE=10 && \
	export FIRESTORE_EMULATOR_HOST=127.0.0.1:8081 && \
	export GOOGLE_CLOUD_PROJECT=test-project && \
	export PYTHONPATH=functions/processor && \
	poetry run pytest tests/test_units_transaction_operations.py

test_units_fee_calculator.py:
	export EVENT_MAX_AGE=10 && \
	export PYTHONPATH=functions/processor && \
	poetry run pytest tests/test_units_fee_calculator.py

test_units_card_order_fee_calculator.py:
	# cd emulators && firebase emulators:start activate emulator
	# gcp-storage-emulator start
	export PYTHONPATH=cloud_run_service/main && \
	poetry run pytest tests/test_units_card_order_fee_calculator.py

test_integration_dataflow.py:
	export FIRESTORE_EMULATOR_HOST=127.0.0.1:8081 && \
	export GOOGLE_CLOUD_PROJECT=test-project && \
	export PYTHONPATH=dataflow && \
	export STORAGE_EMULATOR_HOST=http://localhost:9023 && \
	poetry run pytest tests/test_integration_dataflow.py --bucket test-bucket --date 2024-10-01
