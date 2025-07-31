SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

CREATE OR ALTER   PROCEDURE [dbo].[sp_hubspot_update]
AS
BEGIN 
    SET NOCOUNT ON;
    
    -- ========================================================================
    -- 📋 CREACIÓN/VERIFICACIÓN DE TABLA DE DESTINO
    -- ========================================================================
    
    PRINT '🚀 Iniciando proceso de actualización de datos para HubSpot...'
    
    -- Verificar si la tabla existe, si no, crearla
    IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[update_contacts_hs]') AND type in (N'U'))
    BEGIN
        PRINT '📋 Creando tabla update_contacts_hs...'
        
        CREATE TABLE [dbo].[update_contacts_hs] (
            [sync_id] [int] IDENTITY(1,1) NOT NULL,
            [sync_timestamp] [datetime] NOT NULL DEFAULT GETDATE(),
            
            -- 🔑 CAMPOS PRINCIPALES (Mapeo directo con HubSpot)
            [numero_asociado] [varchar](20) NULL,
            [no__de_cedula] [varchar](20) NOT NULL,
            [firstname] [varchar](100) NULL,
            [lastname] [varchar](200) NULL,
            [email] [varchar](255) NULL,
            [email_bncr] [varchar](255) NULL,
            
            -- 📱 CAMPOS DE CONTACTO
            [hs_whatsapp_phone_number] [varchar](20) NULL,
            [telefono_habitacion] [varchar](20) NULL,
            [telefono_oficina] [varchar](20) NULL,
            
            -- 👤 INFORMACIÓN PERSONAL
            [date_of_birth] [date] NULL,
            [marital_status] [varchar](50) NULL,
            [cantidad_hijos] [int] NULL,
            [estado_asociado] [varchar](20) NULL,
            [fecha_ingreso] [date] NULL,
            [puesto] [varchar](100) NULL,
            [institucion] [varchar](100) NULL,
            [departamento] [varchar](100) NULL,
            
            -- 💰 INFORMACIÓN FINANCIERA
            [salario_bruto_semanal_o_quincenal] [decimal](18,2) NULL,
            [salario_neto_semanal_o_quincenal] [decimal](18,2) NULL,
            
            -- 🌍 UBICACIÓN GEOGRÁFICA
            [provincia] [varchar](50) NULL,
            [canton] [varchar](50) NULL,
            [distrito] [varchar](50) NULL,
            
            -- 💳 PRODUCTOS FINANCIEROS - AHORROS
            [con_ahorros] [varchar](5) NULL,
            [tiene_economias] [varchar](5) NULL,
            [tiene_ahorro_navideno] [varchar](5) NULL,
            [tiene_plan_fin_de_ano] [varchar](5) NULL,
            [tiene_ahorro_fondo_de_inversion] [varchar](5) NULL,
            [tiene_ahorro_plan_vacacional] [varchar](5) NULL,
            [tiene_ahorro_plan_aguinaldo] [varchar](5) NULL,
            [tiene_ahorro_plan_bono_escolar] [varchar](5) NULL,
            [tiene_ahorro_con_proposito] [varchar](5) NULL,
            [tiene_ahorro_plan_futuro] [varchar](5) NULL,
            
            -- 💳 PRODUCTOS FINANCIEROS - CRÉDITOS
            [con_creditos] [varchar](5) NULL,
            [sobre_capital_social] [varchar](5) NULL,
            [adelanto_de_pension_sf] [varchar](5) NULL,
            [ahorros_credito] [varchar](5) NULL,
            [consumo_personal] [varchar](5) NULL,
            [salud] [varchar](5) NULL,
            [adelanto_de_pension_pf] [varchar](5) NULL,
            [especiales_al_vencimiento] [varchar](5) NULL,
            [facilito] [varchar](5) NULL,
            [vehiculos_no_usar] [varchar](5) NULL,
            [credito_refinanciamiento] [varchar](5) NULL,
            [refundicion_de_pasivos] [varchar](5) NULL,
            [vivienda_patrimonial] [varchar](5) NULL,
            [credito_capitalizable] [varchar](5) NULL,
            [capitalizable_2] [varchar](5) NULL,
            [refundicion_ii] [varchar](5) NULL,
            [capitalizable_3] [varchar](5) NULL,
            [tecnologico] [varchar](5) NULL,
            [credifacil] [varchar](5) NULL,
            [vivienda_cooperativa] [varchar](5) NULL,
            [vivienda_adjudicados] [varchar](5) NULL,
            [multiuso] [varchar](5) NULL,
            [deuda_unica] [varchar](5) NULL,
            [vivienda_constructivo] [varchar](5) NULL,
            [credito_compra_vehiculos] [varchar](5) NULL,
            [credito_vehiculos_seminuevos] [varchar](5) NULL,
            [con_back_to_back] [varchar](5) NULL,
            
            -- 🛡️ SEGUROS
            [tiene_seguros] [varchar](5) NULL,
            [apoyo_funerario] [varchar](5) NULL,
            [seguro_su_vida] [varchar](5) NULL,
            [funeraria_polini] [varchar](5) NULL,
            [poliza_colectiva] [varchar](5) NULL,
            [plan_medismart] [varchar](5) NULL,
            [poliza_vivienda] [varchar](5) NULL,
            
            -- 🏦 OTROS PRODUCTOS
            [tiene_cesantia] [varchar](5) NULL,
            [tiene_certificados] [varchar](5) NULL,
            [encargado] [varchar](100) NULL,
            
            -- 🔄 CONTROL DE SINCRONIZACIÓN CON HUBSPOT
            [last_modified] [datetime] NULL DEFAULT GETDATE(),
            [hubspot_sync_status] [varchar](20) NULL DEFAULT 'PENDING',
            [hubspot_contact_id] [varchar](50) NULL,
            [sync_attempts] [int] NULL DEFAULT 0,
            [last_sync_attempt] [datetime] NULL,
            [sync_error_message] [varchar](max) NULL,
            
            CONSTRAINT [PK_update_contacts_hs] PRIMARY KEY CLUSTERED ([sync_id] ASC),
            CONSTRAINT [IX_update_contacts_hs_cedula] UNIQUE NONCLUSTERED ([no__de_cedula] ASC)
        );
        
        PRINT '✅ Tabla update_contacts_hs creada exitosamente con todos los campos.'
    END
    ELSE
    BEGIN
        PRINT '📋 Tabla update_contacts_hs ya existe - procediendo con actualización.'
    END
    
    -- ========================================================================
    -- 🧹 LIMPIAR DATOS EXISTENTES
    -- ========================================================================
    
    PRINT '🧹 Limpiando datos existentes...'
    DELETE FROM [dbo].[update_contacts_hs];
    DECLARE @deleted_count INT = @@ROWCOUNT;
    PRINT '✅ ' + CAST(@deleted_count AS VARCHAR(10)) + ' registros anteriores eliminados.'
    
    -- ========================================================================
    -- 📥 INSERTAR DATOS FRESCOS - CONSERVANDO TODA LA LÓGICA ORIGINAL
    -- ========================================================================
    
    PRINT '📥 Insertando datos actualizados desde sistema cooperativa...';
    
    with 
    -- � CTE para deduplicación eficiente usando ROW_NUMBER
    [AsociadosUnicos] as (
        select *,
            ROW_NUMBER() OVER (
                PARTITION BY REPLACE(REPLACE(REPLACE(REPLACE(ccedulasoc, '-', ''), ' ', ''), '.', ''), ',', '')
                ORDER BY 
                    CASE WHEN ccondasoci = '01' THEN 0 ELSE 1 END,
                    dfechainga DESC
            ) as rn
        from covicoopebanacio.dbo.asmaestras
        where ccedulasoc IS NOT NULL 
          AND ccedulasoc != ''
          AND REPLACE(REPLACE(REPLACE(REPLACE(ccedulasoc, '-', ''), ' ', ''), '.', ''), ',', '') != '00000000'
    ),
    CorreoP as (
    select 
        cidasociad,
        cemailasoc as correo
    from [AsociadosUnicos]
    where cemailasoc not like '%bncr%'
        and cemailasoc like '%@%'
        and rn = 1  -- Solo el registro principal por cédula

    union

    select 
        cidasociad,
        cemailaso2 as correo
    from [AsociadosUnicos]
    where cemailaso2 not like '%bncr%'
        and cemailaso2 like '%@%'
        and rn = 1  -- Solo el registro principal por cédula
        and cidasociad not in (
            select cidasociad
            from [AsociadosUnicos]
            where cemailasoc not like '%bncr%'
                and cemailasoc like '%@%'
                and rn = 1
        )
),
[CorreoBN] as (
    select 
        cidasociad,
        cemailasoc as correo
    from [AsociadosUnicos]
    where cemailasoc like '%bncr%'
        and cemailasoc like '%@%'
        and rn = 1  -- Solo el registro principal por cédula

    union

    select 
        cidasociad,
        cemailaso2 as correo
    from [AsociadosUnicos]
    where cemailaso2 like '%bncr%'
        and cemailaso2 like '%@%'
        and rn = 1  -- Solo el registro principal por cédula
        and cidasociad not in (
            select cidasociad
            from [AsociadosUnicos]
            where cemailasoc like '%bncr%'
                and cemailasoc like '%@%'
                and rn = 1
        )
    ),
[Provincias] as (
        select
            t1.aso_cidasociad
            ,t2.nom_provi
            ,t2.cod_provi
        from proce.dbo.asoc_activos t1
        inner join proce.dbo.provincias t2 on t1.aso_cod_provi = t2.cod_provi
    ),
[Cantones] as (
        select
            t1.aso_cidasociad
            ,t2.nom_canton
            ,t2.id_canton
        from proce.dbo.asoc_activos t1
        inner join proce.dbo.cantones t2 on t1.aso_id_canton = t2.id_canton
    ),
[Distritos] as (
        select
            t1.aso_cidasociad
            ,t2.nom_distrit
            ,t2.id_distrito
        from proce.dbo.asoc_activos t1
        inner join proce.dbo.distritos t2 on t1.aso_id_distrito= t2.id_distrito
    ),
[Con Ahorros] as (
        select 
            t1.cidasociad
           ,'si' as [Ahorros]
        from covicoopebanacio.dbo.dededucaso t1
        left join covicoopebanacio.dbo.asmaestras t2 on t1.cidasociad = t2.cidasociad
        where t1.nmtocuotas >'0' AND
            t1.ccoddeducc in ('9999','0003','0017','0027','0019','0028','0023','0029','0035','0036','0037','0038') and
            t2.ccondasoci = '01'
        group by t1.cidasociad
    ),
[Economias] as (
        select 
            t1.cidasociad
           ,'si' as [Ahorros]
        from covicoopebanacio.dbo.dededucaso t1
        left join covicoopebanacio.dbo.asmaestras t2 on t1.cidasociad = t2.cidasociad
        where t1.nmtocuotas >'0' AND
            t1.ccoddeducc = '9999' and
            t2.ccondasoci = '01'
        group by t1.cidasociad
    ),
[Navideno] as (
        select 
            t1.cidasociad
           ,'si' as [Ahorros]
        from covicoopebanacio.dbo.dededucaso t1
        left join covicoopebanacio.dbo.asmaestras t2 on t1.cidasociad = t2.cidasociad
        where t1.nmtocuotas >'0' AND
            t1.ccoddeducc = '0003' and
            t2.ccondasoci = '01'
        group by t1.cidasociad
    ),
[PFin de Año] as (
        select distinct
            t1.cidasociad
           ,'si' as [Ahorros]
        from covicoopebanacio.dbo.dededucaso t1
        left join covicoopebanacio.dbo.asmaestras t2 on t1.cidasociad = t2.cidasociad
        where t1.nmtocuotas >'0' AND
            t1.ccoddeducc in ('0017','0027') and
            t2.ccondasoci = '01'
        group by t1.cidasociad
    ),
[Fondo de Inversion] as (
        select distinct
            t1.cidasociad
           ,'si' as [Ahorros]
        from covicoopebanacio.dbo.dededucaso t1
        left join covicoopebanacio.dbo.asmaestras t2 on t1.cidasociad = t2.cidasociad
        where t1.nmtocuotas >'0' AND
            t1.ccoddeducc in ('0019','0028') and
            t2.ccondasoci = '01'
        group by t1.cidasociad
    ),
[Plan Vacacional] as (
        select distinct
            t1.cidasociad
           ,'si' as [Ahorros]
        from covicoopebanacio.dbo.dededucaso t1
        left join covicoopebanacio.dbo.asmaestras t2 on t1.cidasociad = t2.cidasociad
        where t1.nmtocuotas >'0' AND
            t1.ccoddeducc in ('0023','0029') and
            t2.ccondasoci = '01'
        group by t1.cidasociad
    ),
[Aguinaldo] as (
        select distinct
            t1.cidasociad
           ,'si' as [Ahorros]
        from covicoopebanacio.dbo.dededucaso t1
        left join covicoopebanacio.dbo.asmaestras t2 on t1.cidasociad = t2.cidasociad
        where t1.nmtocuotas >'0' AND
            t1.ccoddeducc in ('0035') and
            t2.ccondasoci = '01'
        group by t1.cidasociad
    ),
[Bono Escolar] as (
        select distinct
            t1.cidasociad
           ,'si' as [Ahorros]
        from covicoopebanacio.dbo.dededucaso t1
        left join covicoopebanacio.dbo.asmaestras t2 on t1.cidasociad = t2.cidasociad
        where t1.nmtocuotas >'0' AND
            t1.ccoddeducc in ('0036') and
            t2.ccondasoci = '01'
        group by t1.cidasociad
    ),
[Proposito] as (
        select distinct
            t1.cidasociad
           ,'si' as [Ahorros]
        from covicoopebanacio.dbo.dededucaso t1
        left join covicoopebanacio.dbo.asmaestras t2 on t1.cidasociad = t2.cidasociad
        where t1.nmtocuotas >'0' AND
            t1.ccoddeducc in ('0037') and
            t2.ccondasoci = '01'
        group by t1.cidasociad
    ),
[Plan Futuro] as (
        select distinct
            t1.cidasociad
           ,'si' as [Ahorros]
        from covicoopebanacio.dbo.dededucaso t1
        left join covicoopebanacio.dbo.asmaestras t2 on t1.cidasociad = t2.cidasociad
        where t1.nmtocuotas >'0' AND
            t1.ccoddeducc in ('0038') and
            t2.ccondasoci = '01'
        group by t1.cidasociad
    ),
    --CONTABILIZA EL TEMA DE LOS CRÉDITOS
[Con Créditos] as (
        select 
            t1.cidasociad
           ,'si' as [Creditos]
        from covicoopebanacio.dbo.crprestamo t1
        left join covicoopebanacio.dbo.asmaestras t2 on t1.cidasociad = t2.cidasociad
        where t1.nsaldocred >'0' AND
            t2.ccondasoci = '01'
        group by t1.cidasociad
    ),
[Capital] as (
        select 
            t1.cidasociad
           ,'si' as [Creditos]
        from covicoopebanacio.dbo.crprestamo t1
        left join covicoopebanacio.dbo.asmaestras t2 on t1.cidasociad = t2.cidasociad
        where t1.nsaldocred >'0' AND
            t2.ccondasoci = '01' AND
            t1.ccodigolin = '0000000001'
        group by t1.cidasociad
    ),
[AdelantoSF] as (
        select 
            t1.cidasociad
           ,'si' as [Creditos]
        from covicoopebanacio.dbo.crprestamo t1
        left join covicoopebanacio.dbo.asmaestras t2 on t1.cidasociad = t2.cidasociad
        where t1.nsaldocred >'0' AND
            t2.ccondasoci = '01' AND
            t1.ccodigolin = '0000000005'
        group by t1.cidasociad
    ),
[Ahorros***] as (
        select 
            t1.cidasociad
           ,'si' as [Creditos]
        from covicoopebanacio.dbo.crprestamo t1
        left join covicoopebanacio.dbo.asmaestras t2 on t1.cidasociad = t2.cidasociad
        where t1.nsaldocred >'0' AND
            t2.ccondasoci = '01' AND
            t1.ccodigolin = '0000000026'
        group by t1.cidasociad
    ),
[Consumo] as (
        select 
            t1.cidasociad
           ,'si' as [Creditos]
        from covicoopebanacio.dbo.crprestamo t1
        left join covicoopebanacio.dbo.asmaestras t2 on t1.cidasociad = t2.cidasociad
        where t1.nsaldocred >'0' AND
            t2.ccondasoci = '01' AND
            t1.ccodigolin = '0000000027'
        group by t1.cidasociad
    ),
[Salud] as (
        select 
            t1.cidasociad
           ,'si' as [Creditos]
        from covicoopebanacio.dbo.crprestamo t1
        left join covicoopebanacio.dbo.asmaestras t2 on t1.cidasociad = t2.cidasociad
        where t1.nsaldocred >'0' AND
            t2.ccondasoci = '01' AND
            t1.ccodigolin = '0000000028'
        group by t1.cidasociad
    ),
[PensionPF] as (
        select 
            t1.cidasociad
           ,'si' as [Creditos]
        from covicoopebanacio.dbo.crprestamo t1
        left join covicoopebanacio.dbo.asmaestras t2 on t1.cidasociad = t2.cidasociad
        where t1.nsaldocred >'0' AND
            t2.ccondasoci = '01' AND
            t1.ccodigolin = '0000000029'
        group by t1.cidasociad
    ),
[Especiales] as (
        select 
            t1.cidasociad
           ,'si' as [Creditos]
        from covicoopebanacio.dbo.crprestamo t1
        left join covicoopebanacio.dbo.asmaestras t2 on t1.cidasociad = t2.cidasociad
        where t1.nsaldocred >'0' AND
            t2.ccondasoci = '01' AND
            t1.ccodigolin = '0000000030'
        group by t1.cidasociad
    ),
[Facilito] as (
        select 
            t1.cidasociad
           ,'si' as [Creditos]
        from covicoopebanacio.dbo.crprestamo t1
        left join covicoopebanacio.dbo.asmaestras t2 on t1.cidasociad = t2.cidasociad
        where t1.nsaldocred >'0' AND
            t2.ccondasoci = '01' AND
            t1.ccodigolin = '0000000033'
        group by t1.cidasociad
    ),
[VehiculosNo] as (
        select 
            t1.cidasociad
           ,'si' as [Creditos]
        from covicoopebanacio.dbo.crprestamo t1
        left join covicoopebanacio.dbo.asmaestras t2 on t1.cidasociad = t2.cidasociad
        where t1.nsaldocred >'0' AND
            t2.ccondasoci = '01' AND
            t1.ccodigolin = '0000000035'
        group by t1.cidasociad
    ),
[Refinanciamiento] as (
        select 
            t1.cidasociad
           ,'si' as [Creditos]
        from covicoopebanacio.dbo.crprestamo t1
        left join covicoopebanacio.dbo.asmaestras t2 on t1.cidasociad = t2.cidasociad
        where t1.nsaldocred >'0' AND
            t2.ccondasoci = '01' AND
            t1.ccodigolin = '0000000038'
        group by t1.cidasociad
    ),
[Refundicion] as (
        select 
            t1.cidasociad
           ,'si' as [Creditos]
        from covicoopebanacio.dbo.crprestamo t1
        left join covicoopebanacio.dbo.asmaestras t2 on t1.cidasociad = t2.cidasociad
        where t1.nsaldocred >'0' AND
            t2.ccondasoci = '01' AND
            t1.ccodigolin = '0000000039'
        group by t1.cidasociad
    ),
[ViviendaP] as (
        select 
            t1.cidasociad
           ,'si' as [Creditos]
        from covicoopebanacio.dbo.crprestamo t1
        left join covicoopebanacio.dbo.asmaestras t2 on t1.cidasociad = t2.cidasociad
        where t1.nsaldocred >'0' AND
            t2.ccondasoci = '01' AND
            t1.ccodigolin = '0000000041'
        group by t1.cidasociad
    ),
[capitalizable] as (
        select 
            t1.cidasociad
           ,'si' as [Creditos]
        from covicoopebanacio.dbo.crprestamo t1
        left join covicoopebanacio.dbo.asmaestras t2 on t1.cidasociad = t2.cidasociad
        where t1.nsaldocred >'0' AND
            t2.ccondasoci = '01' AND
            t1.ccodigolin = '0000000042'
        group by t1.cidasociad
    ),
[Capitalizable2] as (
        select 
            t1.cidasociad
           ,'si' as [Creditos]
        from covicoopebanacio.dbo.crprestamo t1
        left join covicoopebanacio.dbo.asmaestras t2 on t1.cidasociad = t2.cidasociad
        where t1.nsaldocred >'0' AND
            t2.ccondasoci = '01' AND
            t1.ccodigolin = '0000000047'
        group by t1.cidasociad
    ),
[Refundicion2] as (
        select 
            t1.cidasociad
           ,'si' as [Creditos]
        from covicoopebanacio.dbo.crprestamo t1
        left join covicoopebanacio.dbo.asmaestras t2 on t1.cidasociad = t2.cidasociad
        where t1.nsaldocred >'0' AND
            t2.ccondasoci = '01' AND
            t1.ccodigolin = '0000000051'
        group by t1.cidasociad
    ),
[capitalizable3] as (
        select 
            t1.cidasociad
           ,'si' as [Creditos]
        from covicoopebanacio.dbo.crprestamo t1
        left join covicoopebanacio.dbo.asmaestras t2 on t1.cidasociad = t2.cidasociad
        where t1.nsaldocred >'0' AND
            t2.ccondasoci = '01' AND
            t1.ccodigolin = '0000000053'
        group by t1.cidasociad
    ),
[Tecnologico] as (
        select 
            t1.cidasociad
           ,'si' as [Creditos]
        from covicoopebanacio.dbo.crprestamo t1
        left join covicoopebanacio.dbo.asmaestras t2 on t1.cidasociad = t2.cidasociad
        where t1.nsaldocred >'0' AND
            t2.ccondasoci = '01' AND
            t1.ccodigolin = '0000000054'
        group by t1.cidasociad
    ),
[Credifacil] as (
        select 
            t1.cidasociad
           ,'si' as [Creditos]
        from covicoopebanacio.dbo.crprestamo t1
        left join covicoopebanacio.dbo.asmaestras t2 on t1.cidasociad = t2.cidasociad
        where t1.nsaldocred >'0' AND
            t2.ccondasoci = '01' AND
            t1.ccodigolin = '0000000055'
        group by t1.cidasociad
    ),
[ViviendaCop] as (
        select 
            t1.cidasociad
           ,'si' as [Creditos]
        from covicoopebanacio.dbo.crprestamo t1
        left join covicoopebanacio.dbo.asmaestras t2 on t1.cidasociad = t2.cidasociad
        where t1.nsaldocred >'0' AND
            t2.ccondasoci = '01' AND
            t1.ccodigolin = '0000000056'
        group by t1.cidasociad
    ),
[ViviendaAD] as (
        select 
            t1.cidasociad
           ,'si' as [Creditos]
        from covicoopebanacio.dbo.crprestamo t1
        left join covicoopebanacio.dbo.asmaestras t2 on t1.cidasociad = t2.cidasociad
        where t1.nsaldocred >'0' AND
            t2.ccondasoci = '01' AND
            t1.ccodigolin = '0000000057'
        group by t1.cidasociad
    ),
[Multiuso] as (
        select 
            t1.cidasociad
           ,'si' as [Creditos]
        from covicoopebanacio.dbo.crprestamo t1
        left join covicoopebanacio.dbo.asmaestras t2 on t1.cidasociad = t2.cidasociad
        where t1.nsaldocred >'0' AND
            t2.ccondasoci = '01' AND
            t1.ccodigolin = '0000000058'
        group by t1.cidasociad
    ),
[DeudaUnica] as (
        select 
            t1.cidasociad
           ,'si' as [Creditos]
        from covicoopebanacio.dbo.crprestamo t1
        left join covicoopebanacio.dbo.asmaestras t2 on t1.cidasociad = t2.cidasociad
        where t1.nsaldocred >'0' AND
            t2.ccondasoci = '01' AND
            t1.ccodigolin = '0000000062'
        group by t1.cidasociad
    ),
[ViviendaCons] as (
        select 
            t1.cidasociad
           ,'si' as [Creditos]
        from covicoopebanacio.dbo.crprestamo t1
        left join covicoopebanacio.dbo.asmaestras t2 on t1.cidasociad = t2.cidasociad
        where t1.nsaldocred >'0' AND
            t2.ccondasoci = '01' AND
            t1.ccodigolin = '0000000068'
        group by t1.cidasociad
    ),
[Vehiculo] as (
        select 
            t1.cidasociad
           ,'si' as [Creditos]
        from covicoopebanacio.dbo.crprestamo t1
        left join covicoopebanacio.dbo.asmaestras t2 on t1.cidasociad = t2.cidasociad
        where t1.nsaldocred >'0' AND
            t2.ccondasoci = '01' AND
            t1.ccodigolin = '0000000069'
        group by t1.cidasociad
    ),
[Seminuevos] as (
        select 
            t1.cidasociad
           ,'si' as [Creditos]
        from covicoopebanacio.dbo.crprestamo t1
        left join covicoopebanacio.dbo.asmaestras t2 on t1.cidasociad = t2.cidasociad
        where t1.nsaldocred >'0' AND
            t2.ccondasoci = '01' AND
            t1.ccodigolin = '0000000070'
        group by t1.cidasociad
    ),
[BTB] as (
        select 
            t1.cidasociad
           ,'si' as [Creditos]
        from covicoopebanacio.dbo.crprestamo t1
        left join covicoopebanacio.dbo.asmaestras t2 on t1.cidasociad = t2.cidasociad
        where t1.nsaldocred >'0' AND
            t2.ccondasoci = '01' AND
            t1.ccodigolin = '0000000061'
        group by t1.cidasociad
    ),
    --INICIA CONTABILIZACIÓM DE SEGUROS
[Tiene Seguros] as (
        select distinct
            cidasociad
            ,'si' as [Seguros]
        from covicoopebanacio.dbo.dededucaso
        where ccoddeducc in ('0103','0104','0105','0024','0039','0020') and
            nmtocuotas > '0'
    ),
[ApFunerario] as (
        select distinct
            cidasociad
            ,'si' as [Seguros]
        from covicoopebanacio.dbo.dededucaso
        where ccoddeducc = '0103' and
            nmtocuotas > '0'
    ),
[Suvida] as (
        select distinct
            cidasociad
            ,'si' as [Seguros]
        from covicoopebanacio.dbo.dededucaso
        where ccoddeducc = '0104' and
            nmtocuotas > '0'
    ),
[Colectiva] as (
        select distinct
            cidasociad
            ,'si' as [Seguros]
        from covicoopebanacio.dbo.dededucaso
        where ccoddeducc ='0105' and
            nmtocuotas > '0'
    ),
[PoliniF] as (
        select distinct
            cidasociad
            ,'si' as [Seguros]
        from covicoopebanacio.dbo.dededucaso
        where ccoddeducc ='0024' and
            nmtocuotas > '0'
    ),
[Medismart] as (
        select distinct
            cidasociad
            ,'si' as [Seguros]
        from covicoopebanacio.dbo.dededucaso
        where ccoddeducc ='0039' and
            nmtocuotas > '0'
    ),
[Vivienda] as (
        select distinct
            cidasociad
            ,'si' as [Seguros]
        from covicoopebanacio.dbo.dededucaso
        where ccoddeducc ='0020' and
            nmtocuotas > '0'
    ),
    --INDICA SI TIENE CESANTIA
[Cesantia] as (
        select distinct
            cidasociad
            ,'si' as [cesantia]
        from Covicesantia.dbo.dededucaso t1
        where nmtoprinci > '1000'
    ),
    --INDICA SI TIENE CERTIICADOS
[Certificados] as (
        select distinct
            cidasociad
            ,'si' as [Certificados]
        from covicoopebanacio.dbo.ivcerdeppl
        where cestinvers in ('P','I')
    ),
[Encargado] as (
        select DISTINCT
            t1.ccodencarg
            ,t2.cnombrecom
        from covicoopebanacio.dbo.asencargad t1
        inner join covicoopebanacio.dbo.asmaestras t2 on t1.cidasociad = t2.cidasociad
    )

    -- ========================================================================
    -- 📝 INSERT FINAL EN LA TABLA - TODOS LOS CAMPOS MAPEADOS
    -- ========================================================================
    
    INSERT INTO [dbo].[update_contacts_hs] (
        [numero_asociado],
        [no__de_cedula], 
        [firstname],
        [lastname],
        [email],
        [email_bncr],
        [hs_whatsapp_phone_number],
        [telefono_habitacion], 
        [telefono_oficina],
        [date_of_birth],
        [marital_status],
        [cantidad_hijos],
        [estado_asociado],
        [fecha_ingreso],
        [puesto],
        [salario_bruto_semanal_o_quincenal],
        [salario_neto_semanal_o_quincenal],
        [institucion],
        [departamento],
        [provincia],
        [canton],
        [distrito],
        [con_ahorros],
        [tiene_economias],
        [tiene_ahorro_navideno],
        [tiene_plan_fin_de_ano],
        [tiene_ahorro_fondo_de_inversion],
        [tiene_ahorro_plan_vacacional],
        [tiene_ahorro_plan_aguinaldo],
        [tiene_ahorro_plan_bono_escolar],
        [tiene_ahorro_con_proposito],
        [tiene_ahorro_plan_futuro],
        [con_creditos],
        [sobre_capital_social],
        [adelanto_de_pension_sf],
        [ahorros_credito],
        [consumo_personal],
        [salud],
        [adelanto_de_pension_pf],
        [especiales_al_vencimiento],
        [facilito],
        [vehiculos_no_usar],
        [credito_refinanciamiento],
        [refundicion_de_pasivos],
        [vivienda_patrimonial],
        [credito_capitalizable],
        [capitalizable_2],
        [refundicion_ii],
        [capitalizable_3],
        [tecnologico],
        [credifacil],
        [vivienda_cooperativa],
        [vivienda_adjudicados],
        [multiuso],
        [deuda_unica],
        [vivienda_constructivo],
        [credito_compra_vehiculos],
        [credito_vehiculos_seminuevos],
        [con_back_to_back],
        [tiene_seguros],
        [apoyo_funerario],
        [seguro_su_vida],
        [funeraria_polini],
        [poliza_colectiva],
        [plan_medismart],
        [poliza_vivienda],
        [tiene_cesantia],
        [tiene_certificados],
        [encargado]
    )
    SELECT DISTINCT
        t1.cidasociad AS [numero_asociado],
        -- 🔑 Campo clave para HubSpot - LIMPIEZA DE CÉDULA (solo números)
        REPLACE(REPLACE(REPLACE(REPLACE(t1.ccedulasoc, '-', ''), ' ', ''), '.', ''), ',', '') AS [no__de_cedula],
        t1.cnombasoci AS [firstname],
        TRIM(t1.capellido1) + ' ' + RTRIM(t1.capellido2) AS [lastname],
        t2.correo AS [email],
        t3.correo AS [email_bncr],
        case when T1.ctelecelul='22120000' then '0' 
            when T1.ctelecelul ='22122000' then '0' else T1.ctelecelul end AS [hs_whatsapp_phone_number],
        case when t1.cteledomic='22120000' then '0' 
            when t1.cteledomic ='22122000' then '0' else t1.cteledomic end AS [telefono_habitacion],
        case when t1.cteletraba='22120000' then '0' 
            when t1.cteletraba ='22122000' then '0' else t1.cteletraba end AS [telefono_oficina],
        CONVERT(DATE, t1.dfechanaci) AS [date_of_birth],
        t5.cnombestci AS [marital_status],
        t1.ncanthijos AS [cantidad_hijos],
        CASE ccondasoci
            WHEN '01' THEN 'Activo'
            ELSE 'Inactivo' 
        END AS [estado_asociado],
        CONVERT(DATE, t1.dfechainga) AS [fecha_ingreso],
        '' AS [puesto],  -- Campo vacío según original
        t1.nsalarioas AS [salario_bruto_semanal_o_quincenal],
        t1.nsalarione AS [salario_neto_semanal_o_quincenal],
        t6.cnombinsti AS [institucion],
        t4.cnombdepto AS [departamento],
        t7.nom_provi AS [provincia],
        t55.nom_canton AS [canton],
        t56.nom_distrit AS [distrito],
        CASE t8.ahorros WHEN 'si' THEN 'si' ELSE 'no' END AS [con_ahorros],
        CASE t9.ahorros WHEN 'si' THEN 'si' ELSE 'no' END AS [tiene_economias],
        CASE t10.ahorros WHEN 'si' THEN 'si' ELSE 'no' END AS [tiene_ahorro_navideno],
        CASE t11.ahorros WHEN 'si' THEN 'si' ELSE 'no' END AS [tiene_plan_fin_de_ano],
        CASE t12.ahorros WHEN 'si' THEN 'si' ELSE 'no' END AS [tiene_ahorro_fondo_de_inversion],
        CASE t13.ahorros WHEN 'si' THEN 'si' ELSE 'no' END AS [tiene_ahorro_plan_vacacional],
        CASE t14.ahorros WHEN 'si' THEN 'si' ELSE 'no' END AS [tiene_ahorro_plan_aguinaldo],
        CASE t15.ahorros WHEN 'si' THEN 'si' ELSE 'no' END AS [tiene_ahorro_plan_bono_escolar],
        CASE t16.ahorros WHEN 'si' THEN 'si' ELSE 'no' END AS [tiene_ahorro_con_proposito],
        CASE t17.ahorros WHEN 'si' THEN 'si' ELSE 'no' END AS [tiene_ahorro_plan_futuro],
        CASE t18.creditos WHEN 'si' THEN 'si' ELSE 'no' END AS [con_creditos],
        CASE t19.creditos WHEN 'si' THEN 'si' ELSE 'no' END AS [sobre_capital_social],
        CASE t20.creditos WHEN 'si' THEN 'si' ELSE 'no' END AS [adelanto_de_pension_sf],
        CASE t21.creditos WHEN 'si' THEN 'si' ELSE 'no' END AS [ahorros_credito],
        CASE t22.creditos WHEN 'si' THEN 'si' ELSE 'no' END AS [consumo_personal],
        CASE t23.creditos WHEN 'si' THEN 'si' ELSE 'no' END AS [salud],
        CASE t24.creditos WHEN 'si' THEN 'si' ELSE 'no' END AS [adelanto_de_pension_pf],
        CASE t25.creditos WHEN 'si' THEN 'si' ELSE 'no' END AS [especiales_al_vencimiento],
        CASE t26.creditos WHEN 'si' THEN 'si' ELSE 'no' END AS [facilito],
        CASE t27.creditos WHEN 'si' THEN 'si' ELSE 'no' END AS [vehiculos_no_usar],
        CASE t28.creditos WHEN 'si' THEN 'si' ELSE 'no' END AS [credito_refinanciamiento],
        CASE t29.creditos WHEN 'si' THEN 'si' ELSE 'no' END AS [refundicion_de_pasivos],
        CASE t30.creditos WHEN 'si' THEN 'si' ELSE 'no' END AS [vivienda_patrimonial],
        CASE t31.creditos WHEN 'si' THEN 'si' ELSE 'no' END AS [credito_capitalizable],
        CASE t32.creditos WHEN 'si' THEN 'si' ELSE 'no' END AS [capitalizable_2],
        CASE t33.creditos WHEN 'si' THEN 'si' ELSE 'no' END AS [refundicion_ii],
        CASE t34.creditos WHEN 'si' THEN 'si' ELSE 'no' END AS [capitalizable_3],
        CASE t35.creditos WHEN 'si' THEN 'si' ELSE 'no' END AS [tecnologico],
        CASE t36.creditos WHEN 'si' THEN 'si' ELSE 'no' END AS [credifacil],
        CASE t37.creditos WHEN 'si' THEN 'si' ELSE 'no' END AS [vivienda_cooperativa],
        CASE t38.creditos WHEN 'si' THEN 'si' ELSE 'no' END AS [vivienda_adjudicados],
        CASE t39.creditos WHEN 'si' THEN 'si' ELSE 'no' END AS [multiuso],
        CASE t40.creditos WHEN 'si' THEN 'si' ELSE 'no' END AS [deuda_unica],
        CASE t41.creditos WHEN 'si' THEN 'si' ELSE 'no' END AS [vivienda_constructivo],
        CASE t42.creditos WHEN 'si' THEN 'si' ELSE 'no' END AS [credito_compra_vehiculos],
        CASE t51.creditos WHEN 'si' THEN 'si' ELSE 'no' END AS [credito_vehiculos_seminuevos],
        CASE t43.creditos WHEN 'si' THEN 'si' ELSE 'no' END AS [con_back_to_back],
        CASE t44.Seguros WHEN 'si' THEN 'si' ELSE 'no' END AS [tiene_seguros],
        CASE t45.Seguros WHEN 'si' THEN 'si' ELSE 'no' END AS [apoyo_funerario],
        CASE t46.Seguros WHEN 'si' THEN 'si' ELSE 'no' END AS [seguro_su_vida],
        CASE t52.Seguros WHEN 'si' THEN 'si' ELSE 'no' END AS [funeraria_polini],
        CASE t47.Seguros WHEN 'si' THEN 'si' ELSE 'no' END AS [poliza_colectiva],
        CASE t53.Seguros WHEN 'si' THEN 'si' ELSE 'no' END AS [plan_medismart],
        CASE t54.Seguros WHEN 'si' THEN 'si' ELSE 'no' END AS [poliza_vivienda],
        CASE t48.cesantia WHEN 'si' THEN 'si' ELSE 'no' END AS [tiene_cesantia],
        CASE t49.Certificados WHEN 'si' THEN 'si' ELSE 'no' END AS [tiene_certificados],
        CASE
            WHEN t6.cnombinsti = 'COOPEBANACIO' THEN '000'
            ELSE t50.cnombrecom 
        END AS [encargado]
    FROM [AsociadosUnicos] t1 
    LEFT JOIN [CorreoP] t2 ON t1.cidasociad = t2.cidasociad
    LEFT JOIN [CorreoBN] t3 ON t1.cidasociad = t3.cidasociad
    LEFT JOIN covicoopebanacio.dbo.asdepartam t4 ON t1.cinstdepto = t4.cinstdepto
    LEFT JOIN covicoopebanacio.dbo.asestadoci t5 ON t1.cestadociv = t5.cestadociv
    LEFT JOIN covicoopebanacio.dbo.asinttrab t6 ON t1.cinstuasoc = t6.cinstasoc
    LEFT JOIN [Provincias] t7 ON t1.cidasociad = t7.aso_cidasociad
    LEFT JOIN [Con Ahorros] t8 ON t1.cidasociad = t8.cidasociad
    LEFT JOIN [Economias] t9 ON t1.cidasociad = t9.cidasociad
    LEFT JOIN [Navideno] t10 ON t1.cidasociad = t10.cidasociad
    LEFT JOIN [PFin de Año] t11 ON t1.cidasociad = t11.cidasociad
    LEFT JOIN [Fondo de Inversion] t12 ON t1.cidasociad = t12.cidasociad
    LEFT JOIN [Plan Vacacional] t13 ON t1.cidasociad = t13.cidasociad
    LEFT JOIN [Aguinaldo] t14 ON t1.cidasociad = t14.cidasociad
    LEFT JOIN [Bono Escolar] t15 ON t1.cidasociad = t15.cidasociad
    LEFT JOIN [Proposito] t16 ON t1.cidasociad = t16.cidasociad
    LEFT JOIN [Plan Futuro] t17 ON t1.cidasociad = t17.cidasociad
    LEFT JOIN [Con Créditos] t18 ON t1.cidasociad = t18.cidasociad
    LEFT JOIN [Capital] t19 ON t1.cidasociad = t19.cidasociad
    LEFT JOIN [AdelantoSF] t20 ON t1.cidasociad = t20.cidasociad
    LEFT JOIN [Ahorros***] t21 ON t1.cidasociad = t21.cidasociad
    LEFT JOIN [Consumo] t22 ON t1.cidasociad = t22.cidasociad
    LEFT JOIN [Salud] t23 ON t1.cidasociad = t23.cidasociad
    LEFT JOIN [PensionPF] t24 ON t1.cidasociad = t24.cidasociad
    LEFT JOIN [Especiales] t25 ON t1.cidasociad = t25.cidasociad
    LEFT JOIN [Facilito] t26 ON t1.cidasociad = t26.cidasociad
    LEFT JOIN [VehiculosNo] t27 ON t1.cidasociad = t27.cidasociad
    LEFT JOIN [Refinanciamiento] t28 ON t1.cidasociad = t28.cidasociad
    LEFT JOIN [Refundicion] t29 ON t1.cidasociad = t29.cidasociad
    LEFT JOIN [ViviendaP] t30 ON t1.cidasociad = t30.cidasociad
    LEFT JOIN [capitalizable] t31 ON t1.cidasociad = t31.cidasociad
    LEFT JOIN [Capitalizable2] t32 ON t1.cidasociad = t32.cidasociad
    LEFT JOIN [Refundicion2] t33 ON t1.cidasociad = t33.cidasociad
    LEFT JOIN [capitalizable3] t34 ON t1.cidasociad = t34.cidasociad
    LEFT JOIN [Tecnologico] t35 ON t1.cidasociad = t35.cidasociad
    LEFT JOIN [Credifacil] t36 ON t1.cidasociad = t36.cidasociad
    LEFT JOIN [ViviendaCop] t37 ON t1.cidasociad = t37.cidasociad
    LEFT JOIN [ViviendaAD] t38 ON t1.cidasociad = t38.cidasociad
    LEFT JOIN [Multiuso] t39 ON t1.cidasociad = t39.cidasociad
    LEFT JOIN [DeudaUnica] t40 ON t1.cidasociad = t40.cidasociad
    LEFT JOIN [ViviendaCons] t41 ON t1.cidasociad = t41.cidasociad
    LEFT JOIN [Vehiculo] t42 ON t1.cidasociad = t42.cidasociad
    LEFT JOIN [BTB] t43 ON t1.cidasociad = t43.cidasociad
    LEFT JOIN [Tiene Seguros] t44 ON t1.cidasociad = t44.cidasociad
    LEFT JOIN [ApFunerario] t45 ON t1.cidasociad = t45.cidasociad
    LEFT JOIN [Suvida] t46 ON t1.cidasociad = t46.cidasociad
    LEFT JOIN [Colectiva] t47 ON t1.cidasociad = t47.cidasociad
    LEFT JOIN [Cesantia] t48 ON t1.cidasociad = t48.cidasociad
    LEFT JOIN [Certificados] t49 ON t1.cidasociad = t49.cidasociad
    LEFT JOIN [Encargado] t50 ON t1.ccodencarg = t50.ccodencarg
    LEFT JOIN [Seminuevos] t51 ON t1.cidasociad = t51.cidasociad
    LEFT JOIN [PoliniF] t52 ON t1.cidasociad = t52.cidasociad
    LEFT JOIN [Medismart] t53 ON t1.cidasociad = t53.cidasociad
    LEFT JOIN [Vivienda] t54 ON t1.cidasociad = t54.cidasociad
    LEFT JOIN [Cantones] t55 ON t1.cidasociad = t55.aso_cidasociad
    LEFT JOIN [distritos] t56 ON t1.cidasociad = T56.aso_cidasociad
    WHERE t1.rn = 1  -- � SOLO registros únicos por cédula (el más prioritario)
    
    -- ========================================================================
    -- 📊 REPORTE FINAL Y ESTADÍSTICAS
    -- ========================================================================
    
    DECLARE @total_records INT = @@ROWCOUNT;
    DECLARE @active_records INT;
    DECLARE @inactive_records INT;
    DECLARE @with_email INT;
    DECLARE @with_credits INT;
    DECLARE @with_savings INT;
    
    SELECT @active_records = COUNT(*) 
    FROM [dbo].[update_contacts_hs] 
    WHERE [estado_asociado] = 'Activo';
    
    SELECT @inactive_records = COUNT(*) 
    FROM [dbo].[update_contacts_hs] 
    WHERE [estado_asociado] = 'Inactivo';
    
    SELECT @with_email = COUNT(*) 
    FROM [dbo].[update_contacts_hs] 
    WHERE [email] IS NOT NULL AND [email] != '';
    
    SELECT @with_credits = COUNT(*) 
    FROM [dbo].[update_contacts_hs] 
    WHERE [con_creditos] = 'si';
    
    SELECT @with_savings = COUNT(*) 
    FROM [dbo].[update_contacts_hs] 
    WHERE [con_ahorros] = 'si';
    
    PRINT ''
    PRINT '✅ ==============================================='
    PRINT '🎉 PROCESO COMPLETADO EXITOSAMENTE'
    PRINT '==============================================='
    PRINT '📊 ESTADÍSTICAS FINALES:'
    PRINT '   📈 Total de registros insertados: ' + CAST(@total_records AS VARCHAR(10))
    PRINT '   👥 Asociados activos: ' + CAST(@active_records AS VARCHAR(10))
    PRINT '   😴 Asociados inactivos: ' + CAST(@inactive_records AS VARCHAR(10))
    PRINT '   📧 Con email válido: ' + CAST(@with_email AS VARCHAR(10))
    PRINT '   💳 Con créditos: ' + CAST(@with_credits AS VARCHAR(10))
    PRINT '   💰 Con ahorros: ' + CAST(@with_savings AS VARCHAR(10))
    PRINT '   📅 Timestamp: ' + CONVERT(VARCHAR(19), GETDATE(), 120)
    PRINT ''
    PRINT '🚀 Tabla update_contacts_hs lista para sincronización con HubSpot'
    PRINT '🔑 Campo clave: no__de_cedula (para validación única)'
    PRINT '==============================================='
    
    -- Mostrar muestra de los primeros 5 registros insertados
    PRINT ''
    PRINT '📋 MUESTRA DE REGISTROS INSERTADOS (Primeros 5):'
    
    /* SELECT TOP 5 
        sync_id,
        numero_asociado,
        no__de_cedula,
        firstname,
        lastname,
        email,
        estado_asociado,
        provincia
    FROM [dbo].[hb_contacts_sync]
    ORDER BY sync_id; */
    
END

-- ========================================================================
-- 🚀 COMANDO PARA EJECUTAR EL PROCEDIMIENTO
-- ========================================================================
-- EXEC sp_hubspot_actualizar

GO
