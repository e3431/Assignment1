import streamlit as st
import re
from datetime import datetime
import autogen

# Define the LLM configuration
llm_config = {
    "api_type": "together",
    "model": "meta-llama/llama-Vision-Free",  # Supported model
    "api_key": "tgp_v1_t_wCvAy7jqjE-yrkCSkXjgPoyh6yF7dKVhM8WIvASM8",  # Your API key
    "base_url": "https://api.together.xyz/v1",
    "temperature": 0
}

# Initialize agents
client_intake_agent = autogen.AssistantAgent(
    name="Client Intake Agent",
    system_message="You are an agent responsible for gathering detailed information from the client about the vehicle, including the car's specifications and the customer's details.",
    llm_config=llm_config,  # Using the provided llm_config
)

vehicle_scanning_agent = autogen.AssistantAgent(
    name="Vehicle Scanning Agent",
    system_message="You are responsible for scanning the vehicle using diagnostic devices, collecting data, and generating a comprehensive report about the vehicle's condition.",
    llm_config=llm_config,  # Using the provided llm_config
)

mechanics_analysis_agent = autogen.AssistantAgent(
    name="Mechanics Analysis Agent",
    system_message="You are an agent responsible for reviewing the diagnostic report, assessing the vehicle's condition, and making decisions on necessary repairs or part replacements.",
    llm_config=llm_config,  # Using the provided llm_config
)

quality_control_agent = autogen.AssistantAgent(
    name="Quality Control Technician",
    system_message="You are responsible for inspecting the vehicle after repairs to ensure that all systems are functioning correctly and verifying the repairs.",
    llm_config=llm_config,  # Using the provided llm_config
)

data_storage_agent = autogen.AssistantAgent(
    name="Data Storage Agent",
    system_message="You are responsible for storing vehicle service history in a secure cloud system and ensuring that all data is backed up and accessible for future reference. Additionally, you calculate the date and mileage for the next check-up.",
    llm_config=llm_config,  # Using the provided llm_config
)

# Function to validate each field
def validate_input(vehicle_details, customer_details, service_history):
    # Validate Vehicle Details
    if not all([vehicle_details["Make"], vehicle_details["Model"], vehicle_details["VIN"], vehicle_details["Color"]]):
        st.error("Please fill in all vehicle details (Make, Model, VIN, Color).")
        return False

    if not vehicle_details["Year"].isdigit() or len(vehicle_details["Year"]) != 4:
        st.error("Year must be a valid 4-digit number.")
        return False
    
    if not vehicle_details["Mileage"].isdigit() or int(vehicle_details["Mileage"]) <= 0:
        st.error("Mileage must be a positive number.")
        return False
    
    if not vehicle_details["Seating Capacity"].isdigit() or int(vehicle_details["Seating Capacity"]) <= 0:
        st.error("Seating capacity must be a positive number.")
        return False

    # Validate Customer Details
    if not all([customer_details["Name"], customer_details["Contact"], customer_details["Email"], customer_details["Address"]]):
        st.error("Please fill in all customer details (Name, Contact, Email, Address).")
        return False

    if not re.match(r"^[\d]{10}$", customer_details["Contact"]):
        st.error("Contact number must be a 10-digit number.")
        return False

    if not re.match(r"[^@]+@[^@]+\.[^@]+", customer_details["Email"]):
        st.error("Please enter a valid email address.")
        return False

    # Validate Service History
    if not service_history["Last Service Date"] or not service_history["Next Service Due"]:
        st.error("Please enter valid service dates (Last Service Date and Next Service Due).")
        return False
    
    try:
        datetime.strptime(service_history["Last Service Date"], "%Y-%m-%d")
    except ValueError:
        st.error("Last Service Date must be in the format YYYY-MM-DD.")
        return False
    
    try:
        datetime.strptime(service_history["Next Service Due"], "%Y-%m-%d")
    except ValueError:
        st.error("Next Service Due must be in the format YYYY-MM-DD.")
        return False
    
    if not service_history["Service Mileage"].isdigit() or int(service_history["Service Mileage"]) <= 0:
        st.error("Service mileage must be a positive number.")
        return False

    if not service_history["Service Type"]:
        st.error("Service Type cannot be empty.")
        return False

    return True

# Define the workflow function to be executed in the Streamlit app
def process_workflow(vehicle_details, customer_details, service_history):
    # 1. Client Intake & Initial Assessment
    intake_message = f"Please collect details about the vehicle and client, including the car's specifications, service history, and customer's details. Vehicle: {vehicle_details}, Customer: {customer_details}, Service History: {service_history}"
    intake_response = client_intake_agent.generate_reply(messages=[{"content": intake_message, "role": "user"}])
    st.write(f"**Client Intake Response:** {intake_response['content']}")

    # 2. Vehicle Scanning & Report Generation
    scanning_message = f"Scan the following vehicle details and generate a detailed diagnostic report: {vehicle_details}"
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
    storage_message = f"""
    You are responsible for storing vehicle service history in a secure cloud system and ensuring that all data is backed up and accessible for future reference. 
    Additionally, calculate the date and mileage for the next check-up.
        
    Here are the details:
        
    Customer Info: {customer_details}
    Vehicle Info: {vehicle_details}
    Service History: {service_history}
    Quality Control Report: {quality_control_response['content']}
    """
    storage_response = data_storage_agent.generate_reply(messages=[{"content": storage_message, "role": "user"}])
    st.write(f"**Data Storage Response:** {storage_response['content']}")

    return storage_response

# Streamlit app interface
def run_app():
    st.title("Vehicle Service Workflow")

    # Collect vehicle details (required fields)
    st.header("Vehicle Details")
    vehicle_make = st.text_input("Enter vehicle make", "")
    vehicle_model = st.text_input("Enter vehicle model", "")
    vehicle_year = st.text_input("Enter vehicle year", "")
    vehicle_vin = st.text_input("Enter Vehicle Identification Number (VIN)", "")
    vehicle_color = st.text_input("Enter vehicle color", "")
    vehicle_mileage = st.text_input("Enter vehicle mileage", "")
    vehicle_engine = st.text_input("Enter engine type (e.g., 1.5L Turbo)", "")
    vehicle_transmission = st.text_input("Enter transmission type (e.g., CVT)", "")
    vehicle_fuel_type = st.text_input("Enter fuel type (e.g., Gasoline)", "")
    vehicle_seating_capacity = st.text_input("Enter seating capacity", "")
    vehicle_doors = st.text_input("Enter number of doors", "")
    vehicle_condition = st.text_input("Enter vehicle condition (e.g., Excellent, Good)", "")

    # Collect customer details (required fields)
    st.header("Customer Details")
    customer_name = st.text_input("Enter customer name", "")
    customer_contact = st.text_input("Enter customer contact number", "")
    customer_email = st.text_input("Enter customer email", "")
    customer_address = st.text_input("Enter customer address", "")
    customer_dob = st.text_input("Enter customer date of birth", "")
    customer_license = st.text_input("Enter customer driver's license number", "")
    customer_registration = st.text_input("Enter vehicle registration number", "")
    customer_additional_info = st.text_area("Enter any additional customer information", "")

    # Collect service history details (optional)
    st.header("Service History")
    service_last_date = st.text_input("Enter last service date (YYYY-MM-DD)", "")
    service_next_due = st.text_input("Enter next service due (YYYY-MM-DD)", "")
    service_mileage = st.text_input("Enter service mileage", "")
    service_type = st.text_input("Enter service type (e.g., Oil Change, Tire Rotation)", "")
    service_details = st.text_area("Enter additional service details", "")

    # Button to start the workflow
    if st.button("Start Service Process"):
        # Collect data
        vehicle_details = {
            "Make": vehicle_make,
            "Model": vehicle_model,
            "Year": vehicle_year,
            "VIN": vehicle_vin,
            "Color": vehicle_color,
            "Mileage": vehicle_mileage,
            "Engine": vehicle_engine,
            "Transmission": vehicle_transmission,
            "Fuel Type": vehicle_fuel_type,
            "Seating Capacity": vehicle_seating_capacity,
            "Doors": vehicle_doors,
            "Condition": vehicle_condition
        }

        service_history = {
            "Last Service Date": service_last_date,
            "Next Service Due": service_next_due,
            "Service Mileage": service_mileage,
            "Service Type": service_type,
            "Service Details": service_details
        }

        customer_details = {
            "Name": customer_name,
            "Contact": customer_contact,
            "Email": customer_email,
            "Address": customer_address,
            "Date of Birth": customer_dob,
            "License Number": customer_license,
            "Registration Number": customer_registration,
            "Additional Info": customer_additional_info
        }

        # Validate input
        if validate_input(vehicle_details, customer_details, service_history):
            # Display collected information
            st.subheader("Collected Vehicle Details")
            st.write(vehicle_details)
            st.subheader("Collected Service History")
            st.write(service_history)
            st.subheader("Collected Customer Details")
            st.write(customer_details)

            # Call the workflow function and display results
            with st.spinner('Processing...'):
                result = process_workflow(vehicle_details, customer_details, service_history)
                st.write(f"**Final Workflow Result:** {result['content']}")

# Run the Streamlit app
if __name__ == "__main__":
    run_app()
