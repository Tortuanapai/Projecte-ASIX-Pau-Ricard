import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime
from pathlib import Path
from funciones import get_db_connection


def get_visits_between_dates(start_date, end_date):
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            query = '''
                SELECT 
                    v.id_visita,
                    v.data_visita,
                    v.hora_visita,
                    u.usuario as dni_medico,
                    p.nss,
                    p.nom,
                    p.descripcio,
                    COALESCE(u.nom_rol, 'Sin asignar') as rol_medico
                FROM visites v
                JOIN usuaris_registrats u ON v.id_medico = u.usuario
                JOIN pacients p ON v.id_pacient = p.id_pacient
                WHERE v.data_visita BETWEEN %s AND %s
                ORDER BY v.data_visita, v.hora_visita
            '''
            cur.execute(query, (start_date, end_date))
            rows = cur.fetchall()
            
            visits = []
            for row in rows:
                visits.append({
                    'visit_id': row[0],
                    'date': str(row[1]),
                    'time': str(row[2]) if row[2] else '00:00',
                    'doctor_dni': row[3],
                    'patient_nss': row[4],
                    'patient_name': row[5],
                    'patient_description': row[6],
                    'doctor_role': row[7]
                })
            
            return visits
    except Exception as e:
        raise Exception(f"Error fetching visits: {str(e)}")


def generate_json_export(visits, output_path):
    export_data = {
        'export_info': {
            'export_date': datetime.now().isoformat(),
            'export_type': 'Medical Visits',
            'total_records': len(visits)
        },
        'visits': visits
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=4, ensure_ascii=False)
    
    return output_path


def generate_xml_export(visits, output_path):
    root = ET.Element('VisitsExport')
    
    export_info = ET.SubElement(root, 'ExportInfo')
    ET.SubElement(export_info, 'ExportDate').text = datetime.now().isoformat()
    ET.SubElement(export_info, 'ExportType').text = 'Medical Visits'
    ET.SubElement(export_info, 'TotalRecords').text = str(len(visits))
    
    visits_element = ET.SubElement(root, 'Visits')
    
    for visit in visits:
        visit_elem = ET.SubElement(visits_element, 'Visit')
        
        ET.SubElement(visit_elem, 'VisitID').text = str(visit['visit_id'])
        ET.SubElement(visit_elem, 'Date').text = visit['date']
        ET.SubElement(visit_elem, 'Time').text = visit['time']
        
        doctor = ET.SubElement(visit_elem, 'Doctor')
        ET.SubElement(doctor, 'DNI').text = visit['doctor_dni']
        ET.SubElement(doctor, 'Role').text = visit['doctor_role']
        
        patient = ET.SubElement(visit_elem, 'Patient')
        ET.SubElement(patient, 'NSS').text = visit['patient_nss']
        ET.SubElement(patient, 'Name').text = visit['patient_name']
        ET.SubElement(patient, 'Description').text = visit['patient_description'] or ''
    
    xml_string = minidom.parseString(ET.tostring(root)).toprettyxml(indent='    ')
    xml_string = '\n'.join([line for line in xml_string.split('\n') if line.strip()])
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(xml_string)
    
    return output_path


def generate_json_schema():
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "title": "Medical Visits Export Schema",
        "description": "Schema for exported medical visits data",
        "required": ["export_info", "visits"],
        "properties": {
            "export_info": {
                "type": "object",
                "required": ["export_date", "export_type", "total_records"],
                "properties": {
                    "export_date": {
                        "type": "string",
                        "format": "date-time",
                        "description": "ISO 8601 formatted export timestamp"
                    },
                    "export_type": {
                        "type": "string",
                        "enum": ["Medical Visits"],
                        "description": "Type of exported data"
                    },
                    "total_records": {
                        "type": "integer",
                        "minimum": 0,
                        "description": "Total number of visit records"
                    }
                }
            },
            "visits": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["visit_id", "date", "time", "doctor_dni", "patient_nss", "patient_name"],
                    "properties": {
                        "visit_id": {
                            "type": "integer",
                            "description": "Unique visit identifier"
                        },
                        "date": {
                            "type": "string",
                            "format": "date",
                            "description": "Visit date in YYYY-MM-DD format"
                        },
                        "time": {
                            "type": "string",
                            "pattern": "^([0-1][0-9]|2[0-3]):[0-5][0-9]$",
                            "description": "Visit time in HH:MM format"
                        },
                        "doctor_dni": {
                            "type": "string",
                            "description": "Doctor's DNI identifier"
                        },
                        "patient_nss": {
                            "type": "string",
                            "pattern": "^[0-9]{15}$",
                            "description": "Patient National Health Service number (15 digits)"
                        },
                        "patient_name": {
                            "type": "string",
                            "description": "Patient full name"
                        },
                        "patient_description": {
                            "type": "string",
                            "description": "Patient medical description or notes"
                        },
                        "doctor_role": {
                            "type": "string",
                            "description": "Doctor's professional role"
                        }
                    }
                }
            }
        }
    }
    
    return schema


def generate_xsd_schema():
    xsd_content = '''<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <xs:element name="VisitsExport">
        <xs:complexType>
            <xs:sequence>
                <xs:element name="ExportInfo" type="ExportInfoType"/>
                <xs:element name="Visits" type="VisitsType"/>
            </xs:sequence>
        </xs:complexType>
    </xs:element>

    <xs:complexType name="ExportInfoType">
        <xs:sequence>
            <xs:element name="ExportDate" type="xs:dateTime"/>
            <xs:element name="ExportType" type="xs:string"/>
            <xs:element name="TotalRecords" type="xs:integer"/>
        </xs:sequence>
    </xs:complexType>

    <xs:complexType name="VisitsType">
        <xs:sequence>
            <xs:element name="Visit" type="VisitType" minOccurs="0" maxOccurs="unbounded"/>
        </xs:sequence>
    </xs:complexType>

    <xs:complexType name="VisitType">
        <xs:sequence>
            <xs:element name="VisitID" type="xs:integer"/>
            <xs:element name="Date" type="xs:date"/>
            <xs:element name="Time" type="xs:time"/>
            <xs:element name="Doctor" type="DoctorType"/>
            <xs:element name="Patient" type="PatientType"/>
        </xs:sequence>
    </xs:complexType>

    <xs:complexType name="DoctorType">
        <xs:sequence>
            <xs:element name="DNI" type="xs:string"/>
            <xs:element name="Role" type="xs:string"/>
        </xs:sequence>
    </xs:complexType>

    <xs:complexType name="PatientType">
        <xs:sequence>
            <xs:element name="NSS" type="xs:string"/>
            <xs:element name="Name" type="xs:string"/>
            <xs:element name="Description" type="xs:string" minOccurs="0"/>
        </xs:sequence>
    </xs:complexType>
</xs:schema>
'''
    
    return xsd_content


def save_json_schema(output_path):
    schema = generate_json_schema()
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(schema, f, indent=4, ensure_ascii=False)
    return output_path


def save_xsd_schema(output_path):
    schema = generate_xsd_schema()
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(schema)
    return output_path


def export_visits(start_date, end_date, format_type='json'):
    try:
        visits = get_visits_between_dates(start_date, end_date)
        
        if not visits:
            raise Exception("No visits found for the specified date range")
        
        exports_dir = Path('exports')
        exports_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format_type.lower() == 'json':
            json_file = exports_dir / f'visits_export_{timestamp}.json'
            generate_json_export(visits, json_file)
            
            json_schema_file = exports_dir / f'visits_schema_{timestamp}.json'
            save_json_schema(json_schema_file)
            
            return {
                'success': True,
                'format': 'JSON',
                'data_file': str(json_file),
                'schema_file': str(json_schema_file),
                'records': len(visits)
            }
        
        elif format_type.lower() == 'xml':
            xml_file = exports_dir / f'visits_export_{timestamp}.xml'
            generate_xml_export(visits, xml_file)
            
            xsd_schema_file = exports_dir / f'visits_schema_{timestamp}.xsd'
            save_xsd_schema(xsd_schema_file)
            
            return {
                'success': True,
                'format': 'XML',
                'data_file': str(xml_file),
                'schema_file': str(xsd_schema_file),
                'records': len(visits)
            }
        
        else:
            raise ValueError("Format must be 'json' or 'xml'")
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


if __name__ == '__main__':
    pass
