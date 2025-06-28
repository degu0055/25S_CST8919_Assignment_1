<!-- Repo
https://github.com/degu0055/25S_CST8919_Assignment_1
to push git push azure main:master -->



# Flask Auth0 WebApp with Azure Monitoring and Alerting

## Setup Steps

1. **Auth0 Setup:**
   - Create an Auth0 tenant and application.
   - Configure allowed callback URLs to your Azure app URL `/callback`.
   - Get `AUTH0_CLIENT_ID`, `AUTH0_CLIENT_SECRET`, and `AUTH0_DOMAIN`.

2. **Azure Setup:**
   - Deploy your Flask web app to Azure App Service.
   - Create a Log Analytics workspace to collect app logs.
   - Connect your App Service to the Log Analytics workspace for monitoring.

3. **Environment Variables (.env):**
   - Create a `.env` file with:
     ```
     APP_SECRET_KEY=your_flask_secret_key
     AUTH0_CLIENT_ID=your_auth0_client_id
     AUTH0_CLIENT_SECRET=your_auth0_client_secret
     AUTH0_DOMAIN=your_auth0_domain
     PORT=3000
     ```
   - These variables are loaded by the Flask app.

## Logging and Detection Logic

- The Flask app logs important events:
  - User login info (`user_id`, `email`, `timestamp`).
  - Authorized access to `/protected` endpoint with user details (`user_id`, `name`, `ip`, `timestamp`).
  - Unauthorized access attempts.

- Logs are sent to Azure App Service console logs, collected by Log Analytics.

- Detection logic:
  - We analyze logs to find users accessing `/protected` more than 10 times within 15 minutes.
  - Extract `user_id`, `name`, and timestamps from logs.

## KQL Query for Detection

```kql
AppServiceConsoleLogs
| where TimeGenerated > ago(15m)
| where ResultDescription has "event=authorized_access" and ResultDescription has "path=/protected"
| extend user_id = extract(@"user_id=([^\s,]+)", 1, ResultDescription)
| extend name = extract(@"name=\"([^\"]+)\"", 1, ResultDescription)
| extend timestamp = extract(@"timestamp=([^\s,]+)", 1, ResultDescription)
| summarize access_count = count(), latest_timestamp = max(timestamp) by user_id, name
| where access_count > 10
| project user_id, name, latest_timestamp, access_count
| order by access_count desc
```

## Alert Logic

- Created Azure Monitor Alert based on above query.

- Alert triggers if any user accesses `/protected` more than 10 times in 15 minutes.

- Alert severity is set to **3 (Low)**.

- Action Group email notification was skipped as requested.

This setup helps monitor user access patterns and detect possible abuse or suspicious behavior in your Flask Auth0 app hosted on Azure.
