import streamlit as st
import autogen

# Define the LLM configuration
llm_config = {
    "api_type": "together",
    "model": "meta-llama/llama-Vision-Free",  # Supported model
    "api_key": "tgp_v1_t_wCvAy7jqjE-yrkCSkXjgPoyh6yF7dKVhM8WIvASM8",  # Your API key
    "base_url": "https://api.together.xyz/v1",
    "temperature": 0
}

# Client Intake & Initial Assessment Agent
client_intake_agent = autogen.AssistantAgent(
    name="Client Intake Agent",
    system_message="You are an agent responsible for gathering detailed information from the client about the vehicle, including the car's specifications and the customer's details.",
    llm_config=llm_config,  # Using the provided llm_config
)

# Vehicle Scanning & Report Generation Agent
vehicle_scanning_agent = autogen.AssistantAgent(
    name="Vehicle Scanning Agent",
    system_message="You are responsible for scanning the vehicle using diagnostic devices, collecting data, and generating a comprehensive report about the vehicle's condition.",
    llm_config=llm_config,  # Using the provided llm_config
)

# Mechanics Analysis & Decision Making Agent
mechanics_analysis_agent = autogen.AssistantAgent(
    name="Mechanics Analysis Agent",
    system_message="You are an agent responsible for reviewing the diagnostic report, assessing the vehicle's condition, and making decisions on necessary repairs or part replacements.",
    llm_config=llm_config,  # Using the provided llm_config
)

# Quality Control Technician Agent
quality_control_agent = autogen.AssistantAgent(
    name="Quality Control Technician",
    system_message="You are responsible for inspecting the vehicle after repairs to ensure that all systems are functioning correctly and verifying the repairs.",
    llm_config=llm_config,  # Using the provided llm_config
)

# Data Storage & Initialization for Next Check-Up Agent
data_storage_agent = autogen.AssistantAgent(
    name="Data Storage Agent",
    system_message="You are responsible for storing vehicle service history in a secure cloud system and ensuring that all data is backed up and accessible for future reference. Additionally, you calculate the date and mileage for the next check-up.",
    llm_config=llm_config,  # Using the provided llm_config
)

# Define the workflow function to be executed in the Streamlit app
def process_workflow(vehicle_details, customer_details):
    # 1. Client Intake & Initial Assessment
    intake_message = f"Please collect details about the vehicle and client, including the car's specifications, service history, and customer's details. Vehicle: {vehicle_details}, Customer: {customer_details}"
    intake_response = client_intake_agent.generate_reply(messages=[{"content": intake_message, "role": "user"}])
    st.write(f"**Client Intake Response:** {intake_response['content']}")

    # 2. Vehicle Scanning & Report Generation
    scanning_message = "Scan the vehicle's system for issues and generate a detailed diagnostic report."
    scanning_response = vehicle_scanning_agent.generate_reply(messages=[{"content": scanning_message, "role": "user"}])
    st.write(f"**Vehicle Scanning Response:** {scanning_response['content']}")

    # 3. Mechanics Analysis & Decision Making
    analysis_message = f"Review the diagnostic report and make decisions on necessary repairs or replacements. Diagnostic Report: {scanning_response['content']}"
    analysis_response = mechanics_analysis_agent.generate_reply(messages=[{"content": analysis_message, "role": "user"}])
    st.write(f"**Mechanics Analysis Response:** {analysis_response['content']}")

    # 4. Quality Control Technician
    quality_control_message = f"Inspect the vehicle after repairs and ensure all systems are functioning properly. Report the final status after analysis: {analysis_response['content']}"
    quality_control_response = quality_control_agent.generate_reply(messages=[{"content": quality_control_message, "role": "user"}])
    st.write(f"**Quality Control Response:** {quality_control_response['content']}")

    # 5. Data Storage & Initialization for Next Check-Up
    storage_message = f"Store the service history and calculate the next check-up date and mileage. Quality Control Report: {quality_control_response['content']}"
    storage_response = data_storage_agent.generate_reply(messages=[{"content": storage_message, "role": "user"}])
    st.write(f"**Data Storage Response:** {storage_response['content']}")

    return storage_response

# Streamlit app interface
def run_app():
    st.title("Vehicle Service Workflow")

    # Collect vehicle details and customer details from the user
    vehicle_details = st.text_input("Enter vehicle details (e.g., make, model, year)", "Toyota Camry 2020")
    customer_details = st.text_input("Enter customer details (e.g., name, contact info)", "John Doe, 555-1234")

    # Button to start the workflow
    if st.button("Start Service Process"):
        # Call the workflow function and display results
        with st.spinner('Processing...'):
            result = process_workflow(vehicle_details, customer_details)
            st.write(f"**Final Workflow Result:** {result['content']}")

# Run the Streamlit app
if __name__ == "__main__":
    run_app()
