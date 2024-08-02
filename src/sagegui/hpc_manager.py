from fs.sshfs import SSHFS
from fs.ftpfs import FTPFS
from fs.errors import ResourceNotFound, DirectoryExists
from fs.osfs import OSFS
from fs.zipfs import ZipFS
from typing import Any, Dict, List, Literal
import paramiko
from scp import SCPClient
import io
import pandas as pd
import streamlit as st

def create_scp_client(server_ip, username, password):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(server_ip, username=username, password=password)
    return SCPClient(ssh.get_transport()), ssh

class RemoteProjectFileSystem:
    def __init__(self, host: str, user: str, passwd: str, protocol: Literal["ftp", "sftp", "osf"]="sftp"):
        if protocol == "ftp":
            self.fs = FTPFS(host, user, passwd)
            home_path = f"/gpfs/group/yates"  # Adjust as necessary
        elif protocol == "sftp":
            self.fs = SSHFS(host, user=user, passwd=passwd)
            home_path = f"/gpfs/group/yates"  # Adjust as necessary
        elif protocol == "osf":
            self.fs = OSFS(".")
            home_path = "."
        else:
            raise ValueError("Unsupported protocol. Use 'ftp' or 'sftp' or 'osf'")
        
        self._home_path = home_path

        home_fs = self.fs.opendir(home_path)
        if not home_fs.exists("sage_projects"):
            home_fs.makedir("sage_projects")

        self.project_fs = home_fs.opendir("sage_projects")

    def get_fasta_contents(self, project_name: str, file_name: str) -> bytes:
        file_path = f"{project_name}/fasta/{file_name}"
        with self.project_fs.open(file_path, 'rb') as file:
            return file.read()

    def get_spectra_contents(self, project_name: str, file_name: str) -> bytes:
        file_path = f"{project_name}/spectra/{file_name}"
        with self.project_fs.open(file_path, 'rb') as file:
            return file.read()

    def get_results_contents(self, project_name: str, search_name: str) -> bytes:

        directory_path = f"{project_name}/search/{search_name}"

        zip_buffer = io.BytesIO()
        with ZipFS(zip_buffer, write=True) as zip_fs:
            for file_name in self.project_fs.listdir(directory_path):
                file_path = f"{directory_path}/{file_name}"
                with self.project_fs.open(file_path, 'rb') as file:
                    file_contents = file.read()
                    zip_fs.writebytes(file_name, file_contents)

        return zip_buffer.getvalue()

    def create_project(self, project_name: str):
        project_path = f"{project_name}"
        if self.project_fs.exists(project_path):
            raise FileExistsError(f"Project '{project_name}' already exists.")

        project_fs = self.project_fs.makedir(project_path)
        project_fs.makedir("fasta")
        project_fs.makedir("search")
        project_fs.makedir("spectra")

    def remove_project(self, project_name: str):
        project_path = f"{project_name}"
        if self.project_fs.exists(project_path):
            self.project_fs.removetree(project_path)
        else:
            raise ResourceNotFound(f"Project '{project_name}' does not exist.")

    def list_projects(self) -> List[str]:
        return self.project_fs.listdir(".")

    def add_fasta_file(self, project_name: str, file_name: str, data: bytes):
        fasta_path = f"{project_name}/fasta/{file_name}"
        if not self.project_fs.exists(f"{project_name}/fasta"):
            raise ResourceNotFound(f"Project '{project_name}' does not exist or has no 'fasta' directory.")

        with self.project_fs.open(fasta_path, 'wb') as fasta_file:
            fasta_file.write(data)

    def remove_fasta_file(self, project_name: str, file_name: str):
        fasta_path = f"{project_name}/fasta/{file_name}"
        if not self.project_fs.exists(fasta_path):
            raise ResourceNotFound(f"FASTA file '{file_name}' not found in project '{project_name}'.")

        self.project_fs.remove(fasta_path)

    def list_fasta_files(self, project_name: str) -> List[str]:
        fasta_dir = f"{project_name}/fasta"
        if not self.project_fs.exists(fasta_dir):
            raise ResourceNotFound(f"No fasta directory found for project '{project_name}'.")
        return self.project_fs.listdir(fasta_dir)

    def add_spectra(self, project_name: str, file_name: str, data: bytes):
        spectra_path = f"{project_name}/spectra/{file_name}"
        if not self.project_fs.exists(f"{project_name}/spectra"):
            raise ResourceNotFound(f"Project '{project_name}' does not exist or has no 'spectra' directory.")

        with self.project_fs.open(spectra_path, 'wb') as spectra_file:
            spectra_file.write(data)

    def remove_spectra(self, project_name: str, file_name: str):
        spectra_path = f"{project_name}/spectra/{file_name}"
        if not self.project_fs.exists(spectra_path):
            raise ResourceNotFound(f"Spectra '{file_name}' not found in project '{project_name}'.")

        self.project_fs.remove(spectra_path)

    def list_spectra(self, project_name: str) -> List[str]:
        spectra_dir = f"{project_name}/spectra"
        if not self.project_fs.exists(spectra_dir):
            raise ResourceNotFound(f"No spectra directory found for project '{project_name}'.")
        return self.project_fs.listdir(spectra_dir)

    def add_search(self, project_name: str, search_name: str, data: Dict[str, Any], selected_fasta_files, selected_spectra):
        project_dir = f"{project_name}"
        search_dir = f"{project_name}/search/{search_name}"

        # Check if the project exists
        if not self.project_fs.exists(project_dir):
            raise ResourceNotFound(f"Project '{project_name}' does not exist.")

        # Check if the search directory already exists
        if self.project_fs.exists(search_dir):
            raise DirectoryExists(f"Search '{search_name}' already exists in project '{project_name}'.")

        # Create the search directory
        self.project_fs.makedir(search_dir, recreate=True)

        command = ""

        script = f"""
        {command}
"""
        script_replaced = script.replace("\r\n", "\n").replace("\r", "\n")
        script_path = f"{project_name}/search/{search_name}/search_command.sh"

        with self.project_fs.open(script_path, 'w') as search_command_file:
            search_command_file.write(script_replaced)

    def run_search(self, project_name: str, search_name: str):
        scp, ssh = create_scp_client(st.session_state['server_ip'], st.session_state['username'], st.session_state['password'])

        script_path = f"{self._home_path}/sage_projects/{project_name}/search/{search_name}/search_command.sh"

        ssh.exec_command(f"chmod +x {script_path}")
        stdin, stdout, stderr = ssh.exec_command(f"sbatch {script_path}")
        st.write(stderr.read().decode())
        ssh.close()

    def remove_search(self, project_name: str, search_name: str):
        project_dir = f"{project_name}"
        search_dir = f"{project_name}/search/{search_name}"

        # Check if the project exists
        if not self.project_fs.exists(project_dir):
            raise ResourceNotFound(f"Project '{project_name}' does not exist.")

        # Check if the search directory exists
        if not self.project_fs.exists(search_dir):
            raise ResourceNotFound(f"Search '{search_name}' does not exist in project '{project_name}'.")

        # Remove the search directory and its contents
        self.project_fs.removetree(search_dir)

    def list_searches(self, project_name: str) -> List[str]:
        search_dir = f"{project_name}/search"
        if not self.project_fs.exists(search_dir):
            raise ResourceNotFound(f"No search directory found for project '{project_name}'.")
        return self.project_fs.listdir(search_dir)

    def list_results(self, project_name: str, search_name: str) -> List[str]:
        results_dir = f"{project_name}/search/{search_name}"
        if not self.project_fs.exists(results_dir):
            raise ResourceNotFound(f"No results directory found for project '{project_name}'.")
        return self.project_fs.listdir(results_dir)

    def get_results_file_contents(self, project_name: str, search_name: str, file_name: str) -> pd.DataFrame:
        file_path = f"{project_name}/search/{search_name}/{file_name}"

        with self.project_fs.open(file_path, 'rb') as file:
            return pd.read_csv(io.BytesIO(file.read()), sep="\t")

if __name__ == "__main__":
    """
    Testing only, will be not run with streamlit. Must run this file directly to run this code.
    """
    # Connect to FTP server
    password = input("Enter password: ")

    # Alternatively, connect to SFTP server
    pfs = RemoteProjectFileSystem('login02.scripps.edu', 'pgarrett', password, protocol='sftp')

    # Create a new project with metadata
    pfs.create_project('project1')

    # Add a data file to the project
    pfs.add_data_file('project1', 'data1.txt', 'This is some sample data.')

    # List all projects
    projects = pfs.list_projects()
    print(projects)

    # List all data files in a project
    data_files = pfs.list_data_files('project1')
    print(data_files)

    # Add a search to the project
    try:
        pfs.add_search('project1', 'search1', {'param1': 'value1', 'param2': 'value2'})
    except Exception as e:
        print(e)

    # Attempt to add the same search to the project to test error handling
    try:
        pfs.add_search('project1', 'search1', {'param1': 'value1', 'param2': 'value2'})
    except Exception as e:
        print(e)

    print(pfs.get_search_path('project1', 'search1'))

    # Remove the search from the project
    try:
        pfs.remove_search('project1', 'search1')
    except Exception as e:
        print(e)

    # Attempt to remove a non-existent search to test error handling
    try:
        pfs.remove_search('project1', 'search1')
    except Exception as e:
        print(e)

    # Remove a project
    pfs.remove_project('project1')