SELECT
case
        when marital_status = 'Soltero' then '1'
        when marital_status = 'Casado' then '2'
        when marital_status = 'Divorciado' then '3'
        when marital_status = 'Viudo' then '4'
        when marital_status = 'Unión Libre' then '5'
        when marital_status = 'Viudo (a)' then '4'
        when marital_status = 'Divorciado (a)' then '3'
        when marital_status = 'Soltero (a)' then '1'
        when marital_status = 'Casado (a)' then '2'
        else '1' end as [Estado_Civil]
,t1.puesto
,t1.address
,t1.email
,t1.fecha_nacimiento
,getdate() as [Ult. Modificacion]
,dbo.fn_NormalizarNumeroAsociado(t1.numero_asociado, institucion_en_la_que_labora) as [Num.Asociado]
,case
        when dbo.fn_LimpiarTelefono(telefono_oficina) = '22120000' then ' '
        when dbo.fn_LimpiarTelefono(telefono_oficina) = '22122000' then ' '
        else dbo.fn_LimpiarTelefono(telefono_oficina) end as Telef_Oficina
,case
        when dbo.fn_LimpiarTelefono(hs_whatsapp_phone_number) = '22120000' then ' '
        when dbo.fn_LimpiarTelefono(hs_whatsapp_phone_number) = '22122000' then ' '
        else dbo.fn_LimpiarTelefono(hs_whatsapp_phone_number) end AS Celular
,case
        when dbo.fn_LimpiarTelefono(telefono_habitacion) = '22120000' then ' '
        when dbo.fn_LimpiarTelefono(telefono_habitacion) = '22122000' then ' '
        else dbo.fn_LimpiarTelefono(telefono_habitacion) end as Telef_Habitacion
,t1.salario_bruto_semanal_o_quincenal
,t1.salario_neto_semanal_o_quincenal
FROM [dbo].[hb_contacts] t1
where t1.numero_asociado is not null


SELECT top 10 * FROM [dbo].[hb_contacts]

SELECT top 10 * FROM [dbo].[CO_VW_HubSpotContactosNormalizados]