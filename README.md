This guide will walk you through integrating Looker with [Generative AI Studio (Vertex AI)](https://cloud.google.com/vertex-ai/docs/generative-ai/learn/models) via Cloud Functions using the Looker Action API. Users can use the Looker Explore to examine data, then send the Looker query to a Cloud Function, specifying the model prompt and parameters on the form submissions.

There are three Cloud Functions included in this demo that are used to communicate from Looker to Vertex AI via the [Action API](https://github.com/looker-open-source/actions/blob/master/docs/action_api.md):

1. `action_list` - Lists the metadata for the action, including the form and execute endpoints
1. `action_form` - The dynamic form template to presented to users to send parameters to the execute endpoint
1. `action_execute` - The function to run the prediction on the data that is being sent, and send an email

## Installation:

_Before following the steps below, make sure you have enabled the [Secret Manager API](https://console.cloud.google.com/flows/enableapi?apiid=secretmanager.googleapis.com), [Cloud Build API](https://console.cloud.google.com/flows/enableapi?apiid=cloudbuild.googleapis.com), [Cloud Functions API](https://console.cloud.google.com/flows/enableapi?apiid=cloudfunctions.googleapis.com), and the [Vertex AI API](https://console.cloud.google.com/flows/enableapi?apiid=aiplatform.googleapis.com). It will take a few minutes after enabling this APIs for it to propagate through the systems._

_Also make sure you have a Sendgrid account and API key to use for sending emails. You can create a free developer account from the [GCP marketplace](https://console.cloud.google.com/marketplace/details/sendgrid-app/sendgrid-email)._

Use [Cloud Shell](https://cloud.google.com/shell) or the [`gcloud CLI`](https://cloud.google.com/sdk/docs/install) for the following steps.

The two variables you must to modify are:

- `PROJECT` - ID you want to deploy the Cloud Functions to
- `EMAIL_SENDER` - Email address of the sender


1. Clone this repo

   ```
   git clone https://github.com/looker-open-source/vertex-ai-actions
   cd vertex-ai-actions/
   ```
1. Create a copy of `.env.example`, rename it to `.env` and set the variables in `.env`:

   ```
   ACTION_LABEL="Action label"
   ACTION_NAME="ACTION_LABEL"
   REGION="us-central1" # TODO update to your GCP region
   PROJECT="PROJECT_ID"

   SALESFORCE_CLIENT_ID="YOUR_CLIENT_ID"
   SALESFORCE_CLIENT_SECRET="YOUR_CLIENT_SECRET"
   SALESFORCE_USERNAME="YOUR_USERNAME"
   SALESFORCE_PASSWORD="YOUR_PASSWORD"
   ```

1. Generate the LOOKER_AUTH_TOKEN secret. The auth token secret can be any randomly generated string. You can generate such a string with the openssl command:

   ```
   LOOKER_AUTH_TOKEN="`openssl rand -hex 64`"
   ```

1. Run `bash deploy.sh` and wait for the deployment to finish

1. Copy the Action Hub URL (`action_list` endpoint) and the `LOOKER_AUTH_TOKEN` to input into Looker:

   ```
   echo Action Hub URL: https://${REGION}-${PROJECT}.cloudfunctions.net/${ACTION_NAME}-list
   echo LOOKER_AUTH_TOKEN: $LOOKER_AUTH_TOKEN
   ```

1. In Looker, go to the **Admin > Actions** page and click **Add Action Hub**

   - Enter the Action Hub URL
   - click **Configure Authorization** and enter the `LOOKER_AUTH_TOKEN` value for the Authorization Token and click **Enable**
   - Toggle the **Enabled** button and click **Save**

## Troubleshooting:

If the action build fails, you will receive an email notification. Go to the **Admin > Scheduler History** page to view the error message returned from the Action or use `scheduled_plan` System Activity Explore:

- <details><summary> Explore query to see details on action executions: </summary>

  `https://${YOUR_LOOKER_DOMAIN}.com/explore/system__activity/scheduled_plan?fields=scheduled_job.id,scheduled_job.created_time,scheduled_plan_destination.action_type,scheduled_plan_destination.format,scheduled_job.status,scheduled_plan.run_once,scheduled_plan_destination.parameters,scheduled_job.status_detail&f[scheduled_plan_destination.action_type]=vertex-ai&sorts=scheduled_job.created_time+desc&limit=500`

  </details>
