#  Gispo Ltd., hereby disclaims all copyright interest in the program Qaava-qgis-plugin
#  Copyright (C) 2020 Gispo Ltd (https://www.gispo.fi/).
#
#
#  This file is part of Qaava-qgis-plugin.
#
#  Qaava-qgis-plugin is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 2 of the License, or
#  (at your option) any later version.
#
#  Qaava-qgis-plugin is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Qaava-qgis-plugin.  If not, see <https://www.gnu.org/licenses/>.
import binascii
import io
import logging
import re
import zipfile
from typing import Dict, List
from zipfile import ZipFile

from qgis.core import QgsProject

from ...model.land_use_plan import LandUsePlanEnum
from ...qgis_plugin_tools.tools.resources import plugin_name
from ..exceptions import QaavaProjectInInvalidFormat, QaavaProjectNotLoadedException
from .db_utils import get_db_connection_pg_uri

LOGGER = logging.getLogger(plugin_name())


def load_project(project_name: str, plan: LandUsePlanEnum) -> None:
    """
    Load QGIS project from the database
    :param project_name: Name of the project
    :param plan: land use plan
    """
    # noinspection PyArgumentList
    project = QgsProject.instance()
    project.clear()
    uri = get_db_connection_pg_uri(plan, project_name)
    succeeded = project.read(uri)
    if not succeeded:
        raise QaavaProjectNotLoadedException()


def fix_project(auth_cfg_id, conn_params, content):
    """
    Fix data sources from binary representation of zipped QGIS project
    :param conn_params: connection parameters of the db connection
    :param auth_cfg_id: auth config id of the connection
    :param content: SQL file of containing the project(s)
    :return: list of binary QGIS project zip files with correct data sources
    """
    # noinspection SqlResolve
    proj_bytes = [
        line.split(",")[5][4:-3]
        for line in content.split("\n")
        if line.startswith("INSERT INTO public.qgis_projects")
    ]
    byts = [bytes.fromhex(b) for b in proj_bytes]
    ret_vals = fix_data_sources_from_binary_projects(
        conn_params, auth_cfg_id=auth_cfg_id, contents=byts
    )
    for i in range(len(proj_bytes)):
        content = content.replace(proj_bytes[i], ret_vals[i].decode("utf-8"))
    return content


def fix_data_sources_from_binary_projects(
    conn_params: Dict[str, str], auth_cfg_id: str, contents: List[bytes], _test=False
):
    """
    Fix data sources from binary representation of zipped QGIS project
    :param conn_params: connection parameters of the db connection
    :param auth_cfg_id: auth config id of the connection
    :param contents: list of binary QGIS project zip files
    :param _test: whether method is run inside test or not
    :return: list of binary QGIS project zip files with correct data sources
    """
    host = conn_params["host"]
    port = conn_params["port"]
    dbname = conn_params["dbname"]
    ret_vals = []
    conn_string = f"dbname='{dbname}' host={host} port={port} sslmode=disable authcfg={auth_cfg_id} key="
    for i, content in enumerate(contents):
        z = io.BytesIO()
        z.write(content)
        files = extract_zip(z)
        assert len(files) == 2
        qgs_f_key = [f for f in files.keys() if f.endswith(".qgs")][0]
        qgs_proj_content = files[qgs_f_key].decode("utf-8")

        # Replace all connection string from layers with the db specific connection string
        qgs_proj_content = re.sub(
            r"dbname=.*host=.*port=\d{4}.*key=", conn_string, qgs_proj_content
        )
        if _test:
            ret_vals.append(qgs_proj_content)
            continue

        if conn_string not in qgs_proj_content:
            raise QaavaProjectInInvalidFormat()
        files[qgs_f_key] = bytes(qgs_proj_content, "utf-8")
        ret_vals.append(create_in_memory_zip(files))
    return ret_vals


def extract_zip(input_zip):
    input_zip = ZipFile(input_zip)
    return {name: input_zip.read(name) for name in input_zip.namelist()}


def create_in_memory_zip(contents: Dict[str, bytes]) -> bytes:
    zip_buffer = io.BytesIO()
    with ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for file_name, data in contents.items():
            zip_file.writestr(file_name, io.BytesIO(data).getvalue())
    return binascii.hexlify(zip_buffer.getvalue())
