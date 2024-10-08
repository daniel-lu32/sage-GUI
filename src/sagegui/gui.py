from typing import List
import streamlit as st
import pandas as pd
import math

from utils import get_fs
from login import login
import ast

login()

if 'selected_files' not in st.session_state:
    st.session_state.selected_files = []
if 'file_data' not in st.session_state:
    st.session_state.file_data = {}

st.title("sage GUI")

file_system = 'sftp'
if st.session_state.username == 'debug':
    file_system = 'osf'
    
fs = get_fs(st.session_state['server_ip'], st.session_state['username'], st.session_state['password'], file_system)
selected_project = st.selectbox("Select Project:", options=fs.list_projects())

t1, t2, t3, t4, t5 = st.tabs(["Projects", "FASTA Files", "Spectra", "Searches", "View Results"])

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

@st.experimental_dialog("Add FASTA Files")
def fasta_add_dialog(project: str):
    fasta_files = st.file_uploader(label="Upload FASTA Files", type=[".fasta"], accept_multiple_files=True)
    c1, c2 = st.columns(2)
    if c1.button("Confirm", use_container_width=True, type="primary", key="fasta_add_dialog_confirm"):
        for file in fasta_files:
            fs.add_fasta(project, file.name, file.getvalue())
        st.rerun()
    if c2.button("Cancel", use_container_width=True, type="secondary", key="fasta_add_dialog_cancel"):
        st.rerun()

@st.experimental_dialog(f"Are you sure you want to delete these FASTA files?")
def fasta_delete_dialog(project: str, selected_file: str):
    st.dataframe({'Data Files': selected_file}, use_container_width=True, hide_index=True, key='fasta_delete_dialog_df')
    c1, c2 = st.columns(2)
    if c1.button("Confirm", use_container_width=True, type="secondary", key="fasta_delete_dialog_confirm"):
        for file_name in selected_file:
            fs.remove_fasta(project, file_name)
        st.rerun()
    if c2.button("Cancel", use_container_width=True, type="primary", key="fasta_delete_dialog_cancel"):
        st.rerun()

@st.experimental_dialog("Download FASTA File")
def fasta_download_dialog(project: str, selected_file: str):
    new_file_name = st.text_input("Rename File and Press Enter (Include File Extension):", value=selected_file)
    c1, c2 = st.columns(2)
    file_data = fs.get_fasta_contents(project, selected_file)

    c1.download_button(label=f"Download",
                            data=file_data,
                            file_name=new_file_name,
                            mime="application/octet-stream",
                            key=f"fasta_{new_file_name}",
                            use_container_width=True,
                            type="primary"
                        )
    
    if c2.button("Cancel", use_container_width=True, type="secondary", key="fasta_download_dialog_cancel"):
        st.rerun()

with t2:
    if fs.list_projects():
        st.subheader("FASTA Files")
        st.markdown("Click \"Add\" to upload FASTA files. To delete, select FASTA files and click \"Delete.\" To download, select ONE FASTA file and click \"Download.\"")
        df = pd.DataFrame(fs.list_fasta(selected_project), columns=['Name'])
        selection = st.dataframe(df, use_container_width=True, hide_index=True, selection_mode="multi-row", on_select="rerun", key='fasta_files_df')
        selected_indices = [row for row in selection['selection']['rows']]
        selected_files = [df.iloc[i].Name for i in selected_indices]

        if st.button("Add", use_container_width=True, type="primary", key="fasta_add"):
            fasta_add_dialog(selected_project)

        c1, c2 = st.columns(2)
        if c1.button("Delete", use_container_width=True, type="secondary", key="fasta_delete", disabled=len(selected_files) == 0):
            fasta_delete_dialog(selected_project, selected_files)
        if c2.button("Download", use_container_width=True, type="secondary", key="fasta_download", disabled=len(selected_files) != 1):
            fasta_download_dialog(selected_project, selected_files[0])

@st.experimental_dialog("Add Spectra")
def spectra_add_dialog():
    spectra_files = st.file_uploader(label="Upload Spectra", type=[".mzml"], accept_multiple_files=True)
    c1, c2 = st.columns(2)
    if c1.button("Confirm", use_container_width=True, type="primary", key="spectra_add_dialog_confirm"):
        for file in spectra_files:
            fs.add_spectra(selected_project, file.name, file.getvalue())
        st.rerun()
    if c2.button("Cancel", use_container_width=True, type="secondary", key="spectra_add_dialog_cancel"):
        st.rerun()

@st.experimental_dialog(f"Are you sure you want to delete these spectra?")
def spectra_delete_dialog(project: str, selected_file: List[str]):
    st.dataframe({'Spectra': selected_file}, use_container_width=True, hide_index=True, key='spectra_delete_dialog_df')
    c1, c2 = st.columns(2)
    if c1.button("Confirm", use_container_width=True, type="secondary", key="spectra_delete_dialog_confirm"):
        for file_name in selected_file:
            fs.remove_spectra(project, file_name)
        st.rerun()
    if c2.button("Cancel", use_container_width=True, type="primary", key="spectra_delete_dialog_cancel"):
        st.rerun()

@st.experimental_dialog("Download Spectra")
def spectra_download_dialog(project: str, selected_file: str):
    new_file_name = st.text_input("Rename File and Press Enter (Include File Extension):", value=selected_file)
    c1, c2 = st.columns(2)
    file_data = fs.get_spectra_contents(project, selected_file)
    c1.download_button(label=f"Download",
                            data=file_data,
                            file_name=new_file_name,
                            mime="application/octet-stream",
                            key=f"spectra_{new_file_name}",
                            use_container_width=True,
                            type="primary"
                        )
    
    if c2.button("Cancel", use_container_width=True, type="secondary", key="spectra_download_dialog_cancel"):
        st.rerun()

with t3:
    if fs.list_projects():
        st.subheader("Spectra")
        st.markdown("Click \"Add\" to upload spectra. To delete, select spectra and click \"Delete.\" To download, select ONE spectra and click \"Download.\"")
        df = pd.DataFrame(fs.list_spectra(selected_project), columns=['Name'])
        selection = st.dataframe(df, use_container_width=True, hide_index=True, selection_mode="multi-row", on_select='rerun', key='spectra_df')
        selected_indices = [row for row in selection['selection']['rows']]
        selected_files = [df.iloc[i].Name for i in selected_indices]

        if st.button("Add", use_container_width=True, type="primary", key="spectra_add"):
            spectra_add_dialog()

        c1, c2 = st.columns(2)
        if c1.button("Delete", use_container_width=True, type="secondary", key="spectra_delete", disabled=len(selected_files)==0):
            spectra_delete_dialog(selected_project, selected_files)
        if c2.button("Download", use_container_width=True, type="secondary", key="spectra_download", disabled=len(selected_files)!=1):
            spectra_download_dialog(selected_project, selected_files[0])

def convert_to_list(value):
    try:
        return ast.literal_eval(value)
    except (ValueError, SyntaxError):
        return float(value)

def check_modification_syntax(list_of_strings):
    amino_acids = ["A", "C", "D", "E", "F", "G", "H", "I", "K", "L", "M", "N", "P", "Q", "R", "S", "T", "V", "W", "Y"]
    modifiers = ["^", "$", "[", "]"]
    for string in list_of_strings:
        if string == None:
            return False
        elif len(string) == 1:
            if not (string in amino_acids or string in modifiers):
                return False
        elif len(string) == 2:
            if not (string[1] in amino_acids and string[0] in modifiers):
                return False
        else:
            return False
    return True


@st.experimental_dialog("Add Search", width='large')
def search_add_dialog(project: str):

    fasta_df = pd.DataFrame(fs.list_fasta(project), columns=['Name'])
    spectra_df = pd.DataFrame(fs.list_spectra(project), columns=['Name'])

    search_name = st.text_input("Search Name:")

    t1, t2, t3, t4, t5, t6 = st.tabs(['Fragment Index Construction', 'Quantification', 'Search Tolerances', 'Spectral Processing and More', 'FASTA', 'Spectra'])

    with t1:
        search_parameters = {}

        database = {}
        st.subheader("Fragment Index Construction")
        database['bucket_size'] = 2 ** math.floor(math.log2(st.number_input("Bucket Size:", min_value=8192, max_value=65536, value=32768)))


        enzyme = {}
        st.subheader("Enzyme Information")
        c1, c2, c3 = st.columns(3)
        enzyme['missed_cleavages'] = c1.number_input("Missed Cleavages:", value=1)
        enzyme['min_len'] = c2.number_input("Minimum Amino Acid Length:", value=5)
        enzyme['max_len'] = c3.number_input("Maximum Amino Acid Length:", value=50)

        c1, c2 = st.columns(2)
        enzyme['cleave_at'] = c1.text_input("Amino Acids to Cleave at (Leave Blank for Non-Enzymatic, Type \"$\" for No Digestion):", value="KR")
        enzyme['restrict'] = c2.text_input("Do Not Cleave if This Amino Acid Follows Cleavage Site (Single Character Only):", value="P")
        enzyme['c_terminal'] = c1.checkbox("Cleave at C-Terminus of Matching Amino Acid", value=True)
        enzyme['semi_enzymatic'] = c2.checkbox("Perform Semi-Enzymatic Digest", value=False)
        if enzyme['cleave_at'] == "":
            enzyme['cleave_at'] = None
        if enzyme['restrict'] == "":
            enzyme['restrict'] = None
        database['enzyme'] = enzyme

        st.subheader("Fragment Settings")
        c1, c2 = st.columns(2)
        database['fragment_min_mz'] = c1.number_input("Minimum Fragment Mass to Search:", value=150.0)
        database['fragment_max_mz'] = c2.number_input("Maximum Fragment Mass to Search:", value=2000.0)
        database['peptide_min_mass'] = c1.number_input("Minimum Monoisotopic Peptide Mass to Fragment in silico:", value=500.0)
        database['peptide_max_mass'] = c2.number_input("Maximum Monoisotopic Peptide Mass to Fragmentin silico:", value=5000.0)
        database['ion_kinds'] = st.multiselect("Fragment Ions to Produce:", options=["a", "b", "c", "x", "y", "z"], default=["b", "y"])
        database['min_ion_index'] = st.number_input("Minimum Ion Index:", value=2)

        database['static_mods'] = None
        database['variable_mods'] = None

        st.dataframe(pd.DataFrame({"Syntax": ["^X", "$X", "[X", "]X"], "Modification": ["Modification to be applied to amino acid X if it appears at the N-terminus of a peptide", "Modification to be applied to amino acid X if it appears at the C-terminus of a peptide", "Modification to be applied to amino acid X if it appears at the N-terminus of a protein", "Modification to be applied to amino acid X if it appears at the C-terminus of a protein"]}, columns=["Syntax", "Modification"]), use_container_width=True, hide_index=True)

        c1, c2 = st.columns(2)
        c1.subheader("Static Modifications")
        c1.markdown("Enter a one-letter amino acid abbreviation (ACDEFGHIKLMNPQRSTVWY), ^, $, [, or ], OR a combination (see above) in the \"Amino Acid\" column and a decimal in the \"Modification\" column.")
        c2.subheader("Variable Modifications")
        c2.markdown("Enter a one-letter amino acid abbreviation (ACDEFGHIKLMNPQRSTVWY), ^, $, [, or ], OR a combination (see above) in the \"Amino Acid\" column and a LIST of decimals (include hard brackets []) in the \"Modification\" column.")
        static_mods = c1.data_editor(pd.DataFrame(columns=['Amino Acid', 'Modification']), use_container_width=True, num_rows="dynamic", key="static_mods")
        variable_mods = c2.data_editor(pd.DataFrame(columns=['Amino Acid', 'Modification']), use_container_width=True, num_rows="dynamic", key="variable_mods")

        st.subheader("FASTA Database and Decoy Generation")
        c1, c2, c3 = st.columns(3)
        database['max_variable_mods'] = c1.number_input("Maximum Variable Modifications:", value=2)
        database['decoy_tag'] = c2.text_input("Decoy Tag:", value="rev_")
        database['generate_decoys'] = c3.checkbox("Generate Decoys", value=True)

    with t2:
        quant = {}
        st.subheader("Quantification")
        c1, c2, c3 = st.columns(3)
        quant['tmt'] = c1.selectbox("Tandem Mass Tag:", options=[None, "Tmt6", "Tmt10", "Tmt11", "Tmt16", "Tmt18"])
        quant['tmt_settings'] = {
            "level": c2.number_input("MS-Level for TMT Quantification:", value=3),
            "sn": c3.checkbox("Use Signal/Noise Instead of Intensity for TMT Quantification", value=False)
        }
        quant['lfq'] = None
        if st.checkbox("Perform Label-Free Quantification", value=False):
            quant['lfq'] = True

        c1, c2 = st.columns(2)
        quant['lfq_settings'] = {
            "peak_scoring": c1.selectbox("Peak Scoring Method:", options=["Hybrid", "RetentionTime", "SpectralAngle"]),
            "integration": c2.selectbox("Peak Intensity Integration Method:", options=["Sum", "Max"]),
            "spectral_angle": c1.number_input("Normalized Spectral Angle Similarity Measure Threshold:", min_value=0.0, max_value=1.0, value=0.7),
            "ppm_tolerance": c2.number_input("Tolerance for Matching MS1 Ions in PPM:", value=5.0)
        }
        search_parameters['quant'] = quant

    with t3:
        st.subheader("Search Tolerances")
        c1, c2, c3 = st.columns(3)
        precursor_tolerance_type = c1.selectbox("Precursor Tolerance Type", options=["Absolute", "Relative"])
        precursor_tolerance_lower_bound = c2.number_input("Precursor Tolerance Lower Bound:", value=-10.0)
        precursor_tolerance_upper_bound = c3.number_input("Precursor Tolerance Upper Bound:", value=10.0)
        if precursor_tolerance_type == "Absolute":
            search_parameters['precursor_tol'] = {"da": [precursor_tolerance_lower_bound, precursor_tolerance_upper_bound]}
        else:
            search_parameters['precursor_tol'] = {"ppm": [precursor_tolerance_lower_bound, precursor_tolerance_upper_bound]}

        fragment_tolerance_type = c1.selectbox("Fragment Tolerance Type", options=["Absolute", "Relative"])
        fragment_tolerance_lower_bound = c2.number_input("Fragment Tolerance Lower Bound:", value=-10.0)
        fragment_tolerance_upper_bound = c3.number_input("Fragment Tolerance Upper Bound:", value=10.0)
        if fragment_tolerance_type == "Absolute":
            search_parameters['fragment_tol'] = {"da": [fragment_tolerance_lower_bound, fragment_tolerance_upper_bound]}
        else:
            search_parameters['fragment_tol'] = {"ppm": [fragment_tolerance_lower_bound, fragment_tolerance_upper_bound]}

        c1, c2 = st.columns(2)
        search_parameters['precursor_charge'] = [c1.number_input("Precursor Charge States Lower Bound:", value=2), c2.number_input("Precursor Charge States Upper Bound:", value=4)]
        search_parameters['isotope_errors'] = [c1.number_input("Isotope Error of C13 Neutron Lower Bound:", value=0), c2.number_input("Isotope Error of C13 Neutron Upper Bound:", value=0)]
        search_parameters['wide_window'] = st.checkbox("Wide Window Mode", value=False)

    with t4:
        st.subheader("Spectral Processing")
        search_parameters['deisotope'] = st.checkbox("Perform Deisotoping and Charge State Deconvolution on MS2 Spectra", value=False)
        c1, c2 = st.columns(2)
        search_parameters['min_peaks'] = c1.number_input("Only Process MS2 Spectra with At Least This Many Peaks:", value=15)
        search_parameters['max_peaks'] = c2.number_input("Take This Many of the Most Intense MS2 Peaks to Search:", value=150)
        search_parameters['min_matched_peaks'] = c1.number_input("Minimum Number of Matched b/y Ions Required for Scoring and Reporting PSMs:", value=4)
        search_parameters['max_fragment_charge'] = c2.number_input("Maximum Fragment Ion Charge States to Consider (Use Precursor Charge - 1):", min_value=0, value=None)

        st.subheader("Additional Settings")
        c1, c2 = st.columns(2)
        search_parameters['report_psms'] = st.number_input("Number of PSMs to Report for Each Spectrum:", value=1)
        search_parameters['chimera'] = c1.checkbox("Search for Chimeric/Co-Fragmenting PSMs", value=False)
        search_parameters['predict_rt'] = c2.checkbox("Use Retention Time Prediction Model", value=True)

        search_parameters['output_directory'] = f"{fs._home_path}/sage_projects/{project}/search/{search_name}"

    with t5:
        selection = st.dataframe(fasta_df, use_container_width=True, hide_index=True, selection_mode="single-row", on_select="rerun", key='search_fasta_df')
        selected_indices = [row for row in selection['selection']['rows']]
        selected_fasta = [fasta_df.iloc[i].Name for i in selected_indices]
        if len(selected_fasta) == 1:
             selected_fasta= selected_fasta[0]

    with t6:
        selection = st.dataframe(spectra_df, use_container_width=True, hide_index=True, selection_mode="multi-row", on_select="rerun", key='search_spectra_df')
        selected_indices = [row for row in selection['selection']['rows']]
        selected_spectra = [spectra_df.iloc[i].Name for i in selected_indices]

    if not selected_fasta:
        st.warning('No fasta files selected')
    if not search_name:
        st.warning('No search name')
    if not selected_spectra:
        st.warning('No spectra selected')

    if not check_modification_syntax(list(static_mods['Amino Acid'])):
        st.warning('Invalid Static Modifications')
    if not check_modification_syntax(list(variable_mods['Amino Acid'])):
        st.warning('Invalid Variable Modifications')

    c1, c2 = st.columns(2)
    if c1.button("Confirm", use_container_width=True, type="primary", key="search_add_dialog_confirm", disabled=not check_modification_syntax(list(static_mods['Amino Acid'])) or not check_modification_syntax(list(variable_mods['Amino Acid'])) or not selected_fasta or not search_name or not selected_spectra):
        database['fasta'] = f"{fs._home_path}/sage_projects/{project}/fasta/{selected_fasta}"
        if not static_mods.empty:
            static_mods['Modification'] = static_mods['Modification'].apply(convert_to_list)
            database['static_mods'] = static_mods.set_index('Amino Acid')['Modification'].to_dict()
        if not variable_mods.empty:
            variable_mods['Modification'] = variable_mods['Modification'].apply(convert_to_list)
            database['variable_mods'] = variable_mods.set_index('Amino Acid')['Modification'].to_dict()

        search_parameters['database'] = database

        path_list = []
        for spectra in selected_spectra:
            path_list.append(f"{fs._home_path}/sage_projects/{project}/spectra/{spectra}")
        search_parameters['mzml_paths'] = path_list

        fs.add_search(project, search_name, search_parameters)
        fs.run_search(project, search_name)
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

    if c2.button("Cancel", use_container_width=True, type="secondary", key="search_download_dialog_cancel"):
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