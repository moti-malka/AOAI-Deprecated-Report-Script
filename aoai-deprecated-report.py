from azure.identity import DefaultAzureCredential
from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient
import re

# Add your subscription ids here (for example, sub_ids = ["0000-000-00000-0000000-0000", "11111-1111-1111-11111-1111"])
SUB_IDS = []

class Deployment:
    def __init__(self, name, model, subscriptionid, resource_group, resource_id):
        self.name = name
        self.model = model
        self.subscriptionid = subscriptionid
        self.resource_group = resource_group
        self.resource_id = resource_id

deployments = []
def main():
    if not SUB_IDS:
        print("Please add your subscription ids to the SUB_IDS list")
        return
    for sub_id in SUB_IDS:
        print(f"Checking subscription {sub_id}")
        cognitive_client = CognitiveServicesManagementClient(
            credential=DefaultAzureCredential(),
            subscription_id=sub_id
        )
        pattern = r'resourceGroups\/(.*?)\/providers'

        accounts_response = cognitive_client.accounts.list()
        for account in accounts_response:
            match = re.search(pattern, account.id)
            resource_group_name = match.group(1)

            print(f"Checking Azure OpenAI account {account.name}")
            deployments_response = cognitive_client.deployments.list(
                resource_group_name = resource_group_name,
                account_name = account.name
            )
            for deployment in deployments_response:
                deployments.append(Deployment(
                    name=deployment.name,
                    model=deployment.properties.model.name,
                    subscriptionid=sub_id,
                    resource_group=resource_group_name,
                    resource_id=deployment.id
                ))


    save_to_file(deployments)

    print("Done")

def save_to_file(deployments):                          
    # save the deployments to a file as a csv
    with open("deployments.csv", "w") as f:
        f.write("Deployment Name,Model Name,Subscription ID,Resource Group,Resource ID\n")
        for deployment in deployments:
            f.write(f"{deployment.name},{deployment.model},{deployment.subscriptionid},{deployment.resource_group},{deployment.resource_id}\n")


if __name__ == "__main__":
    main()