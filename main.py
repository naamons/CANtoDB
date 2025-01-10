import pandas as pd
import streamlit as st
import os

def parse_excel_to_dbc(data, output_file):
    """Parse the provided Excel data into a DBC format."""
    try:
        # Rename columns based on known structure
        columns = [
            "DB_Type", "DB_Subtype", "Controller", "Specification", "Version", "Tx_Rx",
            "Sender", "Message_Name", "Message_ID", "DLC", "Output", "Latency_Max",
            "Send_Type", "Signal_Name", "Signal_Length", "Start_Bit", "Receiver",
            "Definition", "Description", "Validity", "Multiplexor", "Multiplex", "Timeout",
            "Purpose", "Table", "Error", "Value_Type", "At_Start", "Factor", "Offset",
            "Min", "Max", "Unit", "Signal_Revision", "Comment", "No_Routing", "Extra"
        ]
        data.columns = columns[:len(data.columns)]

        # Filter out invalid Message_IDs
        data = data[data["Message_ID"].apply(lambda x: isinstance(x, str) and x.startswith("0x"))]

        # Prepare DBC content
        dbc_content = []
        dbc_content.append("VERSION \"\"\n")
        dbc_content.append("NS_ :\n")
        dbc_content.append("BS_:\n")

        # Process messages and signals
        for _, row in data.iterrows():
            dbc_content.append(
                f"BO_ {int(row['Message_ID'], 16)} {row['Message_Name']}:{int(row['DLC'])} {row['Sender']}\n"
            )
            dbc_content.append(
                f" SG_ {row['Signal_Name']} : {int(row['Start_Bit'])}|{int(row['Signal_Length'])}@0+ "
                f"({row['Factor']},{row['Offset']}) [{row['Min']}|{row['Max']}] \"{row['Unit']}\"  {row['Receiver']}\n"
            )

        # Write to DBC file
        with open(output_file, "w") as f:
            f.write("\n".join(dbc_content))

        return "\n".join(dbc_content)  # Return content for preview

    except Exception as e:
        st.error(f"Error processing file: {e}")
        return None


# Streamlit app
st.title("Excel to CAN DBC Converter")

st.write("""
Upload an Excel file containing CAN messages and signals, and this app will generate a DBC file for you.
""")

# File uploader
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file:
    try:
        # Read the uploaded Excel file
        excel_data = pd.read_excel(uploaded_file, skiprows=3)
        st.success("Excel file loaded successfully!")
        
        # Generate DBC file
        dbc_output_path = "generated_can_database.dbc"
        dbc_content = parse_excel_to_dbc(excel_data, dbc_output_path)

        if dbc_content:
            st.success("DBC file generated successfully!")
            st.write("### DBC File Preview")
            st.text(dbc_content[:1000])  # Display the first 1000 characters of the DBC file
            
            # Download button for the generated DBC file
            with open(dbc_output_path, "rb") as f:
                st.download_button(
                    label="Download DBC File",
                    data=f,
                    file_name="generated_can_database.dbc",
                    mime="text/plain"
                )

    except Exception as e:
        st.error(f"An error occurred: {e}")
