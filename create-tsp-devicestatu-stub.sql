-- Temporary stub function for tsp_devicestatu to prevent "not found" errors
-- This should be replaced with the full implementation later
-- NOTE: Changed from PROCEDURE to FUNCTION because the Python code expects to iterate over results

CREATE OR REPLACE FUNCTION tcasino.tsp_devicestatu(
    p_mac_address text,
    p_message_type integer,
    p_ip_address text,
    p_version_id integer,
    p_is_sas_port_opened integer,
    p_is_card_reader_working integer,
    p_sas_port text,
    p_card_reader_port text,
    p_machine_status text,
    p_is_device_locked integer,
    p_device_id integer,
    p_play_count integer,
    p_total_bet numeric,
    p_card_machine_log_id integer,
    p_current_page text,
    p_online_count integer,
    p_is_sas_link integer,
    p_customer_id integer,
    p_asset_no integer,
    p_is_bill_acceptor_working integer
)
RETURNS TABLE(
    "IsNewRecord" integer,
    "DeviceId" integer,
    "MachineName" text,
    "IsBonusGives" integer,
    "DeviceTypeId" integer,
    "DeviceTypeGroupId" integer,
    "ScreenTypeId" integer,
    "BillAcceptorTypeId" integer,
    "CashInLimit" numeric,
    "IsPartialTransfer" integer,
    "IsRecordAllSAS" integer,
    "AssetNo" integer,
    "CasinoName" text,
    "IsCanPlayWithoutCard" integer,
    "IsCashless" integer,
    "ScreenRotate" integer,
    "IsBonusCashable" integer,
    "CurrencyCode" text,
    "MachineCurrencyId" integer,
    "CurrencyId" integer,
    "CurrencyRate" numeric,
    "IsAssetNoAlwaysOne" integer,
    "JackpotFactor" numeric,
    "IsPromoAccepts" integer,
    "ProtocolType" integer,
    "CalcBetByTotalCoinIn" integer,
    "GameStartEndNotifications" integer,
    "IsAutoNextVisit" integer,
    "SASVersion" text,
    "PayBackPerc" numeric,
    "WagerBonusFactors" text,
    "CasinoId" integer,
    "AdminCards" text,
    "TicketPrinterTypeId" integer,
    "DefBetFactor" integer,
    "NotifyWonSlot" numeric,
    "NotifyWonRoulette" numeric,
    "JackpotId" integer,
    "NoActivityTimeOutForBillAcceptor" integer,
    "NoActivityTimeForCashoutMoney" integer,
    "NoActivityTimeForCashoutSeconds" integer,
    "MinsToRebootNoNetwork" integer
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Log that the function was called (using correct public schema)
    BEGIN
        INSERT INTO public.device_messages_queue (
            id,
            slot_machine_id, 
            procedure_name,
            payload,
            status,
            created_at
        ) VALUES (
            gen_random_uuid()::text,
            p_mac_address,
            'tsp_devicestatu_stub',
            json_build_object(
                'message_type', p_message_type,
                'device_id', p_device_id,
                'asset_no', p_asset_no,
                'status', 'stub_called'
            )::text,
            'stub_executed',
            NOW()
        );
    EXCEPTION WHEN OTHERS THEN
        -- If logging fails, continue anyway to prevent app crashes
        NULL;
    END;
    
    -- Return device configuration data that the application expects
    RETURN QUERY SELECT 
        1::integer,                              -- IsNewRecord
        COALESCE(p_device_id, 1)::integer,       -- DeviceId
        'Default Machine'::text,                 -- MachineName
        1::integer,                              -- IsBonusGives
        1::integer,                              -- DeviceTypeId
        1::integer,                              -- DeviceTypeGroupId
        1::integer,                              -- ScreenTypeId
        1::integer,                              -- BillAcceptorTypeId
        1000.00::numeric,                        -- CashInLimit
        1::integer,                              -- IsPartialTransfer
        1::integer,                              -- IsRecordAllSAS
        COALESCE(p_asset_no, 1)::integer,        -- AssetNo
        'Casino'::text,                          -- CasinoName
        1::integer,                              -- IsCanPlayWithoutCard
        1::integer,                              -- IsCashless
        0::integer,                              -- ScreenRotate
        1::integer,                              -- IsBonusCashable
        'USD'::text,                             -- CurrencyCode
        1::integer,                              -- MachineCurrencyId
        1::integer,                              -- CurrencyId
        1.0::numeric,                            -- CurrencyRate
        0::integer,                              -- IsAssetNoAlwaysOne
        1.0::numeric,                            -- JackpotFactor
        1::integer,                              -- IsPromoAccepts
        1::integer,                              -- ProtocolType
        1::integer,                              -- CalcBetByTotalCoinIn
        1::integer,                              -- GameStartEndNotifications
        1::integer,                              -- IsAutoNextVisit
        'SAS 6.00'::text,                       -- SASVersion
        85.00::numeric,                          -- PayBackPerc
        ''::text,                                -- WagerBonusFactors
        1::integer,                              -- CasinoId
        ''::text,                                -- AdminCards
        1::integer,                              -- TicketPrinterTypeId
        1::integer,                              -- DefBetFactor
        1000.00::numeric,                        -- NotifyWonSlot
        1000.00::numeric,                        -- NotifyWonRoulette
        1::integer,                              -- JackpotId
        10::integer,                             -- NoActivityTimeOutForBillAcceptor
        10::integer,                             -- NoActivityTimeForCashoutMoney
        10::integer,                             -- NoActivityTimeForCashoutSeconds
        0::integer;                              -- MinsToRebootNoNetwork
    
END;
$$; 