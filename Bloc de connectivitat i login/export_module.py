import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime
from funciones import get_db_connection

def get_visits_data(start_date, end_date):
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            query = '''
                SELECT 
                    v.id_visita,
                    v.data_visita,
                    m.nom as medico_nom,
                    p.nom as paciente_nom,
                    p.cognom1 as paciente_cognom1,
                    p.cognom2 as paciente_cognom2,
                    p.nss as paciente_nss,
                    p.dni as paciente_dni
                FROM visites v
                JOIN medics m ON v.medic_id = m.id_medic
                JOIN pacients p ON v.pacient_id = p.id_pacient
                WHERE DATE(v.data_visita) BETWEEN %s AND %s
                ORDER BY v.data_visita
            '''
            cur.execute(query, (start_date, end_date))
            return cur.fetchall()
    except Exception as e:
        raise Exception(f'Error al obtener datos de visitas: {str(e)}')

def export_to_xml(visits_data, start_date, end_date):
    root = ET.Element('visitas')
    root.set('fecha_exportacion', datetime.now().isoformat())
    root.set('fecha_inicio', str(start_date))
    root.set('fecha_fin', str(end_date))
    
    for visit in visits_data:
        visit_elem = ET.SubElement(root, 'visita')
        
        ET.SubElement(visit_elem, 'id_visita').text = str(visit[0])
        ET.SubElement(visit_elem, 'fecha').text = str(visit[1])
        
        medico_elem = ET.SubElement(visit_elem, 'medico')
        ET.SubElement(medico_elem, 'nombre').text = visit[2]
        
        paciente_elem = ET.SubElement(visit_elem, 'paciente')
        ET.SubElement(paciente_elem, 'nombre').text = visit[3]
        ET.SubElement(paciente_elem, 'apellido1').text = visit[4]
        ET.SubElement(paciente_elem, 'apellido2').text = visit[5] if visit[5] else ''
        ET.SubElement(paciente_elem, 'nss').text = visit[6]
        ET.SubElement(paciente_elem, 'dni').text = visit[7]
    
    xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent='\t')
    return '\n'.join([line for line in xml_str.split('\n') if line.strip()])

def export_to_json(visits_data, start_date, end_date):
    data = {
        'exportacion': {
            'fecha_exportacion': datetime.now().isoformat(),
            'fecha_inicio': str(start_date),
            'fecha_fin': str(end_date),
            'total_visitas': len(visits_data),
            'visitas': []
        }
    }
    
    for visit in visits_data:
        visit_obj = {
            'id_visita': visit[0],
            'fecha': str(visit[1]),
            'medico': {
                'nombre': visit[2]
            },
            'paciente': {
                'nombre': visit[3],
                'apellido1': visit[4],
                'apellido2': visit[5] if visit[5] else '',
                'nss': visit[6],
                'dni': visit[7]
            }
        }
        data['exportacion']['visitas'].append(visit_obj)
    
    return json.dumps(data, indent=4, ensure_ascii=False)

def get_xml_schema():
    xsd = '''<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
	<xs:element name="visitas">
		<xs:complexType>
			<xs:sequence>
				<xs:element name="visita" type="visitaType" maxOccurs="unbounded"/>
			</xs:sequence>
			<xs:attribute name="fecha_exportacion" type="xs:string" use="required"/>
			<xs:attribute name="fecha_inicio" type="xs:date" use="required"/>
			<xs:attribute name="fecha_fin" type="xs:date" use="required"/>
		</xs:complexType>
	</xs:element>
	<xs:complexType name="visitaType">
		<xs:sequence>
			<xs:element name="id_visita" type="xs:integer"/>
			<xs:element name="fecha" type="xs:dateTime"/>
			<xs:element name="medico" type="medicoType"/>
			<xs:element name="paciente" type="pacienteType"/>
		</xs:sequence>
	</xs:complexType>
	<xs:complexType name="medicoType">
		<xs:sequence>
			<xs:element name="nombre" type="xs:string"/>
		</xs:sequence>
	</xs:complexType>
	<xs:complexType name="pacienteType">
		<xs:sequence>
			<xs:element name="nombre" type="xs:string"/>
			<xs:element name="apellido1" type="xs:string"/>
			<xs:element name="apellido2" type="xs:string"/>
			<xs:element name="nss" type="xs:string"/>
			<xs:element name="dni" type="xs:string"/>
		</xs:sequence>
	</xs:complexType>
</xs:schema>'''
    return xsd

def get_json_schema():
    schema = '''{
	"$schema": "http://json-schema.org/draft-07/schema#",
	"type": "object",
	"properties": {
		"exportacion": {
			"type": "object",
			"properties": {
				"fecha_exportacion": {
					"type": "string",
					"format": "date-time"
				},
				"fecha_inicio": {
					"type": "string",
					"format": "date"
				},
				"fecha_fin": {
					"type": "string",
					"format": "date"
				},
				"total_visitas": {
					"type": "integer"
				},
				"visitas": {
					"type": "array",
					"items": {
						"type": "object",
						"properties": {
							"id_visita": {
								"type": "integer"
							},
							"fecha": {
								"type": "string",
								"format": "date-time"
							},
							"medico": {
								"type": "object",
								"properties": {
									"nombre": {
										"type": "string"
									}
								},
								"required": ["nombre"]
							},
							"paciente": {
								"type": "object",
								"properties": {
									"nombre": {
										"type": "string"
									},
									"apellido1": {
										"type": "string"
									},
									"apellido2": {
										"type": "string"
									},
									"nss": {
										"type": "string"
									},
									"dni": {
										"type": "string"
									}
								},
								"required": ["nombre", "apellido1", "nss", "dni"]
							}
						},
						"required": ["id_visita", "fecha", "medico", "paciente"]
					}
				}
			},
			"required": ["fecha_exportacion", "fecha_inicio", "fecha_fin", "total_visitas", "visitas"]
		}
	},
	"required": ["exportacion"]
}'''
    return schema