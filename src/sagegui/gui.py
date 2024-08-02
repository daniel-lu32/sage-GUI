from typing import List
import streamlit as st
import pandas as pd
from utils import get_fs
from login import login

login()

if 'selected_files' not in st.session_state:
    st.session_state.selected_files = []
if 'file_data' not in st.session_state:
    st.session_state.file_data = {}

st.title("DIA-NN GUI")

file_system = 'sftp'
if st.session_state.username == 'debug':
    file_system = 'osf'
    
fs = get_fs(st.session_state['server_ip'], st.session_state['username'], st.session_state['password'], file_system)
selected_project = st.selectbox("Select Project:", options=fs.list_projects())

t1, t2, t3, t4, t5 = st.tabs(["Projects", "Data Files", "Spectral Libraries", "Searches", "View Results"])

@st.experimental_dialog("Add Project")
def projects_add_dialog():
    project_name = st.text_input("Project Name:")
    c1, c2 = st.columns(2)
    if c1.button("Confirm", use_container_width=True, type="primary", key="projects_add_dialog_confirm"):
        fs.create_project(project_name)
        st.rerun()
    if c2.button("Cancel", use_container_width=True, type="secondary", key="projects_add_dialog_cancel"):
        st.rerun()

@st.experimental_dialog(f"Are you sure you want to delete these projects?")
def projects_delete_dialog(selected_projects: List[str]):
    st.dataframe({'Name':selected_projects}, use_container_width=True, hide_index=True, key='project_delete_df')
    c1, c2 = st.columns(2)
    if c1.button("Confirm", use_container_width=True, type="secondary", key="projects_delete_dialog_confirm"):
        for project_name in selected_projects:
            fs.remove_project(project_name)
        st.rerun()
    if c2.button("Cancel", use_container_width=True, type="primary", key="projects_delete_dialog_cancel"):
        st.rerun()

with t1:
    st.subheader("Projects")
    st.markdown("Click \"Add\" to add a project. To delete, select projects and click \"Delete.\"")
    df = pd.DataFrame(fs.list_projects(), columns=['Name'])
    selection = st.dataframe(df, use_container_width=True, hide_index=True, selection_mode="multi-row", on_select="rerun")
    selected_indices = [row for row in selection['selection']['rows']]
    selected_projects = [df.iloc[i].Name for i in selected_indices]

    c1, c2 = st.columns(2)
    if c1.button("Add", use_container_width=True, type="primary", key="projects_add"):
        projects_add_dialog()
    if c2.button("Delete", use_container_width=True, type="secondary", key="projects_delete", disabled=len(selected_projects) == 0):
        projects_delete_dialog(selected_projects)

@st.experimental_dialog("Add Data Files")
def data_add_dialog(project: str):
    data_files = st.file_uploader(label="Upload Data Files", type=[".dia", ".tar", ".zip", ".raw"], accept_multiple_files=True)
    c1, c2 = st.columns(2)
    if c1.button("Confirm", use_container_width=True, type="primary", key="data_add_dialog_confirm"):
        for file in data_files:
            fs.add_data_file(project, file.name, file.getvalue())
        st.rerun()
    if c2.button("Cancel", use_container_width=True, type="secondary", key="data_add_dialog_cancel"):
        st.rerun()

@st.experimental_dialog(f"Are you sure you want to delete these data files?")
def data_delete_dialog(project: str, selected_file: str):
    st.dataframe({'Data Files': selected_file}, use_container_width=True, hide_index=True, key='data_delete_dialog_df')
    c1, c2 = st.columns(2)
    if c1.button("Confirm", use_container_width=True, type="secondary", key="data_delete_dialog_confirm"):
        for file_name in selected_file:
            fs.remove_data_file(project, file_name)
        st.rerun()
    if c2.button("Cancel", use_container_width=True, type="primary", key="data_delete_dialog_cancel"):
        st.rerun()

@st.experimental_dialog("Download Data File")
def data_download_dialog(project: str, selected_file: str):
    new_file_name = st.text_input("Rename File and Press Enter (Include File Extension):", value=selected_file)
    c1, c2 = st.columns(2)
    file_data = fs.get_data_file_contents(project, selected_file)

    c1.download_button(label=f"Download",
                            data=file_data,
                            file_name=new_file_name,
                            mime="application/octet-stream",
                            key=f"data_{new_file_name}",
                            use_container_width=True,
                            type="primary"
                        )
    
    if c2.button("Cancel", use_container_width=True, type="secondary", key="data_download_dialog_cancel"):
        st.rerun()
    

with t2:
    if fs.list_projects():
        st.subheader("Data Files")
        st.markdown("Click \"Add\" to upload data files. To delete, select data files and click \"Delete.\" To download, select ONE data file and click \"Download.\"")
        df = pd.DataFrame(fs.list_data_files(selected_project), columns=['Name'])
        selection = st.dataframe(df, use_container_width=True, hide_index=True, selection_mode="multi-row", on_select="rerun", key='datafiles_df')
        selected_indices = [row for row in selection['selection']['rows']]
        selected_files = [df.iloc[i].Name for i in selected_indices]

        if st.button("Add", use_container_width=True, type="primary", key="data_add"):
            data_add_dialog(selected_project)

        c1, c2 = st.columns(2)
        if c1.button("Delete", use_container_width=True, type="secondary", key="data_delete", disabled=len(selected_files) == 0):
            data_delete_dialog(selected_project, selected_files)
        if c2.button("Download", use_container_width=True, type="secondary", key="data_download", disabled=len(selected_files) != 1):
            data_download_dialog(selected_project, selected_files[0])


@st.experimental_dialog("Add Spectral Libraries")
def spec_lib_add_dialog():
    spec_lib_files = st.file_uploader(label="Upload Spectral Libraries", type=[".txt", ".csv", ".tsv", ".xls", ".speclib", ".sptxt", ".msp"], accept_multiple_files=True)
    c1, c2 = st.columns(2)
    if c1.button("Confirm", use_container_width=True, type="primary", key="spec_lib_add_dialog_confirm"):
        for file in spec_lib_files:
            fs.add_spec_lib(selected_project, file.name, file.getvalue())
        st.rerun()
    if c2.button("Cancel", use_container_width=True, type="secondary", key="spec_lib_add_dialog_cancel"):
        st.rerun()

@st.experimental_dialog(f"Are you sure you want to delete these spectral libraries?")
def spec_lib_delete_dialog(project: str, selected_file: List[str]):
    st.dataframe({'Data Files': selected_file}, use_container_width=True, hide_index=True, key='spec_lib_delete_dialog_df')
    c1, c2 = st.columns(2)
    if c1.button("Confirm", use_container_width=True, type="secondary", key="speclib_delete_dialog_confirm"):
        for file_name in selected_file:
            fs.remove_spec_lib(project, file_name)
        st.rerun()
    if c2.button("Cancel", use_container_width=True, type="primary", key="speclib_delete_dialog_cancel"):
        st.rerun()

@st.experimental_dialog("Download Spectral Library")
def spec_lib_download_dialog(project: str, selected_file: str):
    new_file_name = st.text_input("Rename File and Press Enter (Include File Extension):", value=selected_file)
    c1, c2 = st.columns(2)
    file_data = fs.get_spec_lib_contents(project, selected_file)
    c1.download_button(label=f"Download",
                            data=file_data,
                            file_name=new_file_name,
                            mime="application/octet-stream",
                            key=f"speclib_{new_file_name}",
                            use_container_width=True,
                            type="primary"
                        )
    
    if c2.button("Cancel", use_container_width=True, type="secondary", key="speclib_download_dialog_cancel"):
        st.rerun()

with t3:
    if fs.list_projects():
        st.subheader("Spectral Libraries")
        st.markdown("Click \"Add\" to upload spectral libraries. To delete, select spectral libraries and click \"Delete.\" To download, select ONE spectral library and click \"Download.\"")
        df = pd.DataFrame(fs.list_spec_lib_files(selected_project), columns=['Name'])
        selection = st.dataframe(df, use_container_width=True, hide_index=True, selection_mode="multi-row", on_select='rerun', key='spec_lib_df')
        selected_indices = [row for row in selection['selection']['rows']]
        selected_files = [df.iloc[i].Name for i in selected_indices]

        if st.button("Add", use_container_width=True, type="primary", key="spec_lib_add"):
            spec_lib_add_dialog()

        c1, c2 = st.columns(2)
        if c1.button("Delete", use_container_width=True, type="secondary", key="spec_lib_delete", disabled=len(selected_files)==0):
            spec_lib_delete_dialog(selected_project, selected_files)
        if c2.button("Download", use_container_width=True, type="secondary", key="spec_lib_download", disabled=len(selected_files)!=1):
            spec_lib_download_dialog(selected_project, selected_files[0])


@st.experimental_dialog("Add Search", width='large')
def search_add_dialog(project: str):

    data_df = pd.DataFrame(fs.list_data_files(selected_project), columns=['Name'])
    spec_lib_df = pd.DataFrame(fs.list_spec_lib_files(selected_project), columns=['Name'])

    search_name = st.text_input("Search Name:")

    t1, t2, t3 = st.tabs(['Search Parameters', 'Data Files', 'Spectral Libraries'])

    selected_data_files = []
    selected_spec_lib = None

    with t1:
        search_parameters = {}

        c1, c2 = st.columns(2)
        search_parameters['precursor_fdr'] = c1.number_input("Precursor FDR (%):", min_value=0.01, max_value=100.0, value=1.0)
        search_parameters['log_level'] = c2.number_input("Log Level (%):", min_value=0, max_value=5, value=1)

        search_parameters['quantities_matrices'] = st.checkbox("Quantities Matrices", value=True)
        search_parameters['prosit'] = st.checkbox("Generate Prosit Input from FASTA or Spectral Library", value=False)
        search_parameters['xics'] = st.checkbox("XICs", value=False)

        c1, c2, c3 = st.columns(3)
        search_parameters['mass_accuracy'] = c1.number_input("Mass Accuracy:", min_value=0, max_value=100, value=0)
        search_parameters['ms1_accuracy'] = c2.number_input("MS1 Accuracy:", min_value=0, max_value=100, value=0)
        search_parameters['scan_window'] = c3.number_input("Scan Window:", min_value=0, max_value=1000, value=0)
        
        c1, c2 = st.columns(2)
        search_parameters['unrelated_runs'] = c1.checkbox("Unrelated Runs", value=False)
        search_parameters['peptidoforms'] = c1.checkbox("Peptidoforms", value=False)
        search_parameters['mbr'] = c1.checkbox("MBR", value=False)
        search_parameters['heuristic_protein_interface'] = c2.checkbox("Heuristic Protein Interface", value=True)
        search_parameters['no_shared_spectra'] = c2.checkbox("No Shared Spectra", value=True)

        c1, c2, c3 = st.columns(3)
        search_parameters['protein_inference'] = c1.selectbox("Protein Inference:", options=["Genes", "Isoform IDs", "Protein Names (from FASTA)", "Genes (Species-Specific)", "Off"])
        search_parameters['neural_network_classifier'] = c2.selectbox("Neural Network Classifier:", options=["Single-Pass Mode", "Off", "Double-Pass Mode"])
        search_parameters['quantification_strategy'] = c3.selectbox("Quantification Strategy:", options=["QuantUMS (high precision)", "Legacy (direct)", "QuantUMS (high accuracy)"])
        search_parameters['cross-run_normalization'] = c1.selectbox("Cross-Run Normalization:", options=["RT-dependent", "Global", "RT & signal-dep. (experimental)", "Off"])
        search_parameters['library_generation'] = c2.selectbox("Library Generation:", options=["IDs, RT & IM profiling", "IDs profiling", "Smart profiling", "Full profiling"])
        search_parameters['speed_and_ram_usage'] = c3.selectbox("Speed and RAM Usage", options=["Optimal results", "Low RAM usage", "Low RAM & high speed", "Ultra-fast"])
        search_parameters['additional_options'] = st.text_area("Additional Options:", '')

    with t2:
        selection = st.dataframe(data_df, use_container_width=True, hide_index=True, selection_mode="multi-row", on_select="rerun", key='search_datafiles_df')
        selected_indices = [row for row in selection['selection']['rows']]
        selected_data_files = [data_df.iloc[i].Name for i in selected_indices]

    with t3:
        selection = st.dataframe(spec_lib_df, use_container_width=True, hide_index=True, selection_mode="single-row", on_select="rerun", key='search_speclib_df')
        selected_indices = [row for row in selection['selection']['rows']]
        selected_spec_lib = [spec_lib_df.iloc[i].Name for i in selected_indices]
        if len(selected_spec_lib) == 1:
             selected_spec_lib= selected_spec_lib[0]

    if not selected_data_files:
        st.warning('No data files selected')

    if not search_name:
        st.warning('No search name')

    if not selected_spec_lib:
        st.warning('No spec lib selected')

    c1, c2 = st.columns(2)
    if c1.button("Confirm", use_container_width=True, type="primary", key="search_add_dialog_confirm", disabled= not selected_data_files or not search_name or not selected_spec_lib):
        fs.add_search(selected_project, search_name, search_parameters, selected_data_files, selected_spec_lib)
        fs.run_search(selected_project, search_name)
        st.rerun()
    if c2.button("Cancel", use_container_width=True, type="secondary", key="search_add_dialog_cancel"):
        st.rerun()

@st.experimental_dialog(f"Are you sure you want to delete these searches?")
def search_delete_dialog(project: str, selected_searches: List[str]):
    st.dataframe({'Name': selected_searches}, use_container_width=True, hide_index=True, key='search_delete_dialog_df')
    c1, c2 = st.columns(2)
    if c1.button("Confirm", use_container_width=True, type="secondary", key="search_delete_dialog_confirm"):
        for search in selected_searches:
            fs.remove_search(project, search)
        st.rerun()
    if c2.button("Cancel", use_container_width=True, type="primary", key="search_delete_dialog_cancel"):
        st.rerun()

@st.experimental_dialog("Download Search Results")
def search_download_dialog(project: str, search: str):
    zip_name = st.text_input("Rename Zip and Press Enter (.zip):", value=f"{search}_results.zip")
    c1, c2 = st.columns(2)
    zip_buffer = fs.get_results_contents(project, search)
    c1.download_button(
        label="Download Zip",
        data=zip_buffer,
        file_name=zip_name,
        mime="application/zip",
        key=f"search_{zip_name}",
        use_container_width=True,
        type="primary"
    )

    if c2.button("Cancel", use_container_width=True, type="secondary", key="search_download_dialog_alternative_cancel"):
        st.rerun()

with t4:
    if fs.list_projects():
        st.subheader("Searches")
        st.markdown("Click \"Add\" to configure search parameters and start a new search. To delete, select searches and click \"Delete.\" To download the .zip file containing the search results, select ONE search and click \"Download.\"")
        df = pd.DataFrame(fs.list_searches(selected_project), columns=['Name'])
        selection = st.dataframe(df, use_container_width=True, hide_index=True, selection_mode="multi-row", on_select="rerun", key='search_df')
        selected_indices = [row for row in selection['selection']['rows']]
        selected_files = [df.iloc[i].Name for i in selected_indices]

        if st.button("Add", use_container_width=True, type="primary", key="search_add"):
            search_add_dialog(selected_project)

        c1, c2 = st.columns(2)
        if c1.button("Delete", use_container_width=True, type="secondary", key="search_delete", disabled=len(selected_files) == 0):
            search_delete_dialog(selected_project, selected_files)
        if c2.button("Download", use_container_width=True, type="secondary", key="search_download", disabled=len(selected_files)!=1):
            search_download_dialog(selected_project, selected_files[0])

with t5:
    if fs.list_projects():
        st.subheader("View Results")
        st.markdown("To view search results, select the files you would like to view and click \"View.\"")
        selected_search = st.selectbox("Select Search:", options=fs.list_searches(selected_project))
        if fs.list_searches(selected_project):
            df = pd.DataFrame(fs.list_results(selected_project, selected_search), columns=['Name'])
            selection = st.dataframe(df, use_container_width=True, hide_index=True, selection_mode="multi-row", on_select="rerun", key='results_df')
            selected_indices = [row for row in selection['selection']['rows']]
            selected_files = [df.iloc[i].Name for i in selected_indices]

            if st.button("View", use_container_width=True, type="primary", key="results_view"):
                for file in selected_files:
                    st.caption(file)
                    st.dataframe(data=fs.get_results_file_contents(selected_project, selected_search, file), use_container_width=True, hide_index=True, key='results_view_df')