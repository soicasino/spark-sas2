-- PROCEDURE: tcasino.tsp_checkbillacceptorin(text, bigint, bigint, text, text, text, numeric, text)

-- DROP PROCEDURE IF EXISTS tcasino.tsp_checkbillacceptorin(text, bigint, bigint, text, text, text, numeric, text);

CREATE OR REPLACE PROCEDURE tcasino.tsp_checkbillacceptorin(
	IN p_macaddress text DEFAULT ''::text,
	IN p_billacceptortypeid bigint DEFAULT 0,
	IN p_machinelogid bigint DEFAULT 0,
	IN p_cardno text DEFAULT ''::text,
	IN p_currencycode text DEFAULT ''::text,
	IN p_countrycode text DEFAULT '7B'::text,
	IN p_denom numeric DEFAULT 200,
	IN p_denomhex text DEFAULT ''::text)
LANGUAGE 'plpgsql'
AS $BODY$
DECLARE
    v_result BIGINT := 0;
    v_errormessage TEXT := 'General currency error!';
    v_creditamount NUMERIC := 0;
    v_defcurrencyid BIGINT;
    v_defcurrencycode TEXT;
    v_denomcurrencyid BIGINT;
    v_denomcurrencycode TEXT;
    v_isdenomactive BOOLEAN;
    v_isactiveforfirstinsert BOOLEAN;
    v_defexcrate NUMERIC;
    v_excrate NUMERIC;
BEGIN
    -- This insert into temp_bill assumes a table named temp_bill exists and is accessible.
    -- If it's a temporary table specific to the session, you'd typically define it
    -- or use a CTE for short-lived data. Assuming it's a persistent logging table for now.
    BEGIN
        INSERT INTO temp_bill (
            MacAddress, BillAcceptorTypeId, MachineLogId, CardNo,
            CurrencyCode, CountryCode, Denom, DenomHex
        ) VALUES (
            p_MacAddress, p_BillAcceptorTypeId, p_MachineLogId, p_CardNo,
            p_CurrencyCode, p_CountryCode, p_Denom, p_DenomHex
        );
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'Error inserting into temp_bill: %', SQLERRM;
    END;

    SELECT CurrencyId, Currency
    INTO v_defcurrencyid, v_defcurrencycode
    FROM T_CasinoSettings
    LIMIT 1;

    SELECT CurrencyId, CurrencyCode
    INTO v_denomcurrencyid, v_denomcurrencycode
    FROM T_Currency
    WHERE
        (p_BillAcceptorTypeId = 1 AND BillAcceptorCountryCode = p_CountryCode)
        OR
        (p_BillAcceptorTypeId = 2 AND BillAcceptorCountryCodeMEI = p_CountryCode);

    RAISE NOTICE '@DenomCurrencyId %', v_denomcurrencyid;

    SELECT IsActive, IsActiveForFirstInsert
    INTO v_isdenomactive, v_isactiveforfirstinsert
    FROM T_BankNotes
    WHERE CurrencyId = v_denomcurrencyid AND Denom = p_Denom;

    v_isdenomactive := COALESCE(v_isdenomactive, FALSE);
    v_isactiveforfirstinsert := COALESCE(v_isactiveforfirstinsert, FALSE);

    IF v_denomcurrencyid = v_defcurrencyid THEN
        v_result := 1;
        v_errormessage := p_Denom::TEXT || ' ' || v_denomcurrencycode;
        -- Assuming tcasino.fn_GetAmountWithoutCent is converted
        v_creditamount := tcasino.fn_GetAmountWithoutCent(p_Denom);
    ELSE
        SELECT ExcRate
        INTO v_defexcrate
        FROM T_CurrencyRates
        WHERE TargetCurrencyId = v_defcurrencyid AND SourceCurrencyId = 1; -- Assuming SourceCurrencyId = 1 is a base currency

        SELECT ExcRate
        INTO v_excrate
        FROM T_CurrencyRates
        WHERE TargetCurrencyId = v_defcurrencyid AND SourceCurrencyId = v_denomcurrencyid;
        v_excrate := COALESCE(v_excrate, 0);

        IF v_excrate <> 0 THEN
            v_result := 1;
            v_creditamount := tcasino.fn_GetAmountWithoutCent(p_Denom) * v_excrate;
            v_errormessage := p_Denom::TEXT || ' ' || v_denomcurrencycode || ' => ' || tcasino.fn_GetAmountWithoutCent(v_creditamount)::TEXT || ' ' || v_defcurrencycode;
        ELSE
            SELECT ExcRate
            INTO v_excrate
            FROM T_CurrencyRates
            WHERE TargetCurrencyId = 1 AND SourceCurrencyId = v_denomcurrencyid; -- Assuming TargetCurrencyId = 1 is a base currency
            v_excrate := v_excrate * v_defexcrate;
            v_excrate := COALESCE(v_excrate, 0);

            IF v_excrate <> 0 THEN
                v_result := 1;
                v_creditamount := tcasino.fn_GetAmountWithoutCent(p_Denom) * v_excrate;
                v_errormessage := p_Denom::TEXT || ' ' || v_denomcurrencycode || ' => ' || tcasino.fn_GetAmountWithoutCent(v_creditamount)::TEXT || ' ' || v_defcurrencycode;
            END IF;
        END IF;
    END IF;

    IF v_isdenomactive = FALSE THEN
        v_result := 0;
        v_errormessage := 'Bill is not active! ' || v_errormessage;
    END IF;

    SELECT v_result AS Result, v_errormessage AS ErrorMessage, tcasino.fn_GetAmountWithoutCent(v_creditamount) AS CreditAmount;

END;
$BODY$;
ALTER PROCEDURE tcasino.tsp_checkbillacceptorin(text, bigint, bigint, text, text, text, numeric, text)
    OWNER TO postgres;




-------------------------------



-- Create the PostgreSQL procedure
CREATE OR REPLACE FUNCTION tcasino."tsp_InsBillAcceptorMoney"(
    p_machinelogid     BIGINT,
    p_cardno           VARCHAR,
    p_amount           NUMERIC(19,4),
    p_amountcode       VARCHAR,
    p_macaddress       VARCHAR DEFAULT '',
    p_countrycode      VARCHAR DEFAULT '',
    p_piece            INTEGER DEFAULT 0,
    p_deviceid         BIGINT DEFAULT 0,
    p_islog            BOOLEAN DEFAULT FALSE,
    p_isuploaded       BOOLEAN DEFAULT TRUE,
    p_amountbase       NUMERIC(19,4) DEFAULT 0
)
RETURNS TABLE(result BIGINT, errormessage VARCHAR)
LANGUAGE plpgsql
AS $$
DECLARE
    v_macaddress VARCHAR;
    v_machinecurrencyid BIGINT;
    v_deviceid BIGINT;
    v_amountbase NUMERIC(19,4);
    v_gamingdate DATE;
    v_customerid BIGINT;
    v_countrycode VARCHAR;
    v_billacceptorid BIGINT;
BEGIN
    -- Initialize variables
    v_macaddress := p_macaddress;
    v_deviceid := p_deviceid;
    v_amountbase := p_amountbase;
    v_countrycode := p_countrycode;
    
    -- Get MacAddress if empty
    IF LENGTH(v_macaddress) = 0 THEN
        SELECT macaddress INTO v_macaddress 
        FROM t_device 
        WHERE deviceid = v_deviceid 
        LIMIT 1;
    END IF;
    
    -- Get MachineCurrencyId
    SELECT machinecurrencyid INTO v_machinecurrencyid 
    FROM t_device 
    WHERE deviceid = v_deviceid;
    
    -- Get DeviceId if 0
    IF v_deviceid = 0 THEN
        SELECT deviceid INTO v_deviceid 
        FROM t_device 
        WHERE macaddress = v_macaddress 
        LIMIT 1;
    END IF;
    
    -- Set AmountBase if 0
    IF v_amountbase = 0 THEN
        v_amountbase := p_amount;
    END IF;
    
    -- Get GamingDate
    SELECT gamingdate INTO v_gamingdate 
    FROM t_cardmachinelogs 
    WHERE machinelogid = p_machinelogid 
    LIMIT 1;
    
    SELECT currentgamingdate INTO v_gamingdate 
    FROM t_device 
    WHERE macaddress = v_macaddress;
    
    IF v_gamingdate IS NULL THEN
        -- Assuming fn_GetGamingDate function exists or use CURRENT_DATE
        v_gamingdate := CURRENT_DATE;
    END IF;
    
    -- Get CustomerId
    SELECT customerid INTO v_customerid 
    FROM t_card 
    WHERE cardno = p_cardno;
    
    -- Handle CountryCode
    IF v_countrycode = '00' THEN
        -- Assuming fn_GetDefCurrencyCode function exists or use default
        v_countrycode := 'USD'; -- Replace with actual default currency code
    END IF;
    
    -- Insert into T_DeviceBillAcceptor
    INSERT INTO t_devicebillacceptor (
        machinelogid, cardno, amount, amountcode, macaddress, 
        countrycode, piece, createddate, gamingdate, islog, 
        isuploaded, amountbase
    )
    VALUES (
        p_machinelogid, p_cardno, p_amount, p_amountcode, v_macaddress,
        v_countrycode, p_piece, NOW(), v_gamingdate, p_islog,
        p_isuploaded, v_amountbase
    )
    RETURNING billacceptorid INTO v_billacceptorid;
    
    -- Update T_CardMachineLogs with error handling
    BEGIN
        UPDATE t_cardmachinelogs 
        SET 
            billacceptoramount = COALESCE(billacceptoramount, 0) + p_amount,
            currentbalance = currentbalance + p_amount
        WHERE machinelogid = p_machinelogid;
    EXCEPTION 
        WHEN OTHERS THEN
            -- Silent error handling (equivalent to empty print in MSSQL)
            NULL;
    END;
    
    -- Update T_CustomerAdditional
    UPDATE t_customeradditional 
    SET lastoperationdate = NOW() 
    WHERE customerid = v_customerid;
    
    -- Return result
    RETURN QUERY SELECT v_billacceptorid, ''::VARCHAR;
    
END;
$$



-----------------------------

CREATE OR REPLACE FUNCTION tcasino.tsp_updbillacceptormoney(
    p_billacceptorid bigint,
    p_isuploaded boolean)
    RETURNS TABLE(result integer, errormessage text) 
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
    ROWS 1000

AS $BODY$
BEGIN
    UPDATE tcasino.T_DeviceBillAcceptor SET IsUploaded = p_isuploaded WHERE BillAcceptorId = p_billacceptorid;

    Result := 1;
    ErrorMessage := '';
    RETURN NEXT;

END;
$BODY$;

ALTER FUNCTION tcasino.tsp_updbillacceptormoney(bigint, boolean)
    OWNER TO postgres;
----------------------------------------

-- FUNCTION: tcasino.tsp_cardread(text, text, numeric, numeric, bigint, bigint)

-- DROP FUNCTION IF EXISTS tcasino.tsp_cardread(text, text, numeric, numeric, bigint, bigint);

CREATE OR REPLACE FUNCTION tcasino.tsp_cardread(
    p_macaddress text DEFAULT ''::text,
    p_cardno text DEFAULT ''::text,
    p_customcashable numeric DEFAULT 0,
    p_custompromo numeric DEFAULT 0,
    p_nonamerequest bigint DEFAULT 0,
    p_deviceid bigint DEFAULT 0)
    RETURNS TABLE(result bigint, errormessage text, cardmachinelogid bigint, iscashless integer, deviceid bigint, isnoname bigint, cardid bigint, cardno text, customerid bigint, createddate timestamp without time zone, createdby bigint, modifieddate timestamp without time zone, isactive boolean, cardtype bigint, dedicatedamount numeric, dedicatedpromo numeric, iscustomeractive boolean, fullname text, firstname text, nickname text, bonuspercentage numeric, currentbonus numeric, gender text, totaltruein numeric, totalvisitcount bigint, trackingcode text, canplaymultiplecard boolean, balance numeric, promobalance numeric, uploadmoney bigint, keepbillacceptorclosed bigint, showwarningtime bigint, showwarningheader text, showwarningtext text) 
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
    ROWS 1000

AS $BODY$
DECLARE
    v_gamingday DATE;
    v_cardid BIGINT := 0;
    v_ispromoaccepts BOOLEAN;
    v_cashinlimit NUMERIC;
    v_iscashless INT;
    v_machinecurrencyid BIGINT;
    v_machinetype INT;
    v_iscardhasselfbalance BOOLEAN;
    v_moneylimit NUMERIC;
    v_casinocurrencyid BIGINT;
    v_nonamecustomerid BIGINT;
    v_nonamecardno TEXT;
    v_customerid BIGINT;
    v_iscustomeractive BOOLEAN;
    v_iscardactive BOOLEAN;
    v_trackingcode TEXT;
    v_canplaymultiplecard BOOLEAN := FALSE;
    v_customerfullname TEXT := '';
    v_result BIGINT := 1;
    v_errormessage TEXT := '';
    v_lmacaddress TEXT;
    v_lenterdate TIMESTAMP;
    v_cardtype BIGINT;
    v_uploadmoney BIGINT := 1;
    v_tempmachinelogid BIGINT;
    v_tempexitdate TIMESTAMP;
    v_tempcardno TEXT;
    v_probidedamount NUMERIC;
    v_probidedamountpromoin NUMERIC;
    v_accountid BIGINT;
    v_balance NUMERIC;
    v_promobalance NUMERIC;
    v_cardmachinelogid BIGINT;
    v_currentbalance NUMERIC;
    v_keepbillacceptorclosed BIGINT := 0;
    v_cagecampaignsaleid BIGINT;
    v_cagecampaignid BIGINT;
    v_showwarningtime BIGINT := 0;
    v_showwarningheader TEXT := '';
    v_showwarningtext TEXT := '';
    v_messageimportant TEXT;
    v_normalbalance NUMERIC;
    v_normalpromobalance NUMERIC;
    -- Variables moved from nested DECLARE blocks
    v_isrouletteblacklist BOOLEAN;
    v_isslotblacklist BOOLEAN;
    v_lastuseddate TIMESTAMP;
    v_lastusedsecdiff BIGINT;
BEGIN
    PERFORM PG_SLEEP(0.045);

    IF LENGTH(p_macaddress) = 0 THEN
        p_cardno := '';
    END IF;

    SELECT CurrentGamingDate
    INTO v_gamingday
    FROM tcasino.T_Device
    WHERE DeviceId = p_deviceid;

    IF v_gamingday IS NULL THEN
        SELECT tcasino.fn_getgamingdate(NOW()) INTO v_gamingday;
    END IF;

    SELECT
        DeviceId,
        IsPromoAccepts,
        CashInLimit,
        IsCashless,
        MachineCurrencyId,
        MachineType
    INTO
        p_deviceid,
        v_ispromoaccepts,
        v_cashinlimit,
        v_iscashless,
        v_machinecurrencyid,
        v_machinetype
    FROM tcasino.T_Device
    WHERE DeviceId = p_deviceid
    LIMIT 1;

    p_deviceid := COALESCE(p_deviceid, 0);
    v_cashinlimit := COALESCE(v_cashinlimit, 0);

    IF v_machinecurrencyid IS NULL THEN
        SELECT
            DeviceId,
            IsPromoAccepts,
            CashInLimit,
            IsCashless,
            MachineCurrencyId
        INTO
            p_deviceid,
            v_ispromoaccepts,
            v_cashinlimit,
            v_iscashless,
            v_machinecurrencyid
        FROM tcasino.T_Device
        WHERE DeviceId = p_deviceid
        LIMIT 1;
    END IF;

    SELECT
        IsCardHasSelfBalance,
        MoneyLimit,
        CurrencyId
    INTO
        v_iscardhasselfbalance,
        v_moneylimit,
        v_casinocurrencyid
    FROM tcasino.T_CasinoSettings
    LIMIT 1;

    -- Drop the temporary table if it exists
    BEGIN
        EXECUTE 'DROP TABLE IF EXISTS tempcustomer';
    EXCEPTION
        WHEN OTHERS THEN
            NULL; -- Suppress the notice
    END;

    IF p_nonamerequest = 1 AND LENGTH(p_cardno) = 0 THEN
        BEGIN
            SELECT CustomerId
            INTO v_nonamecustomerid
            FROM tcasino.T_Customer
            WHERE Firstname = 'NONAME' AND LastGamingDate < v_gamingday;

            v_nonamecustomerid := COALESCE(v_nonamecustomerid, 0);

            IF v_nonamecustomerid = 0 THEN
                BEGIN
                    SELECT MAX(CustomerId)
                    INTO v_nonamecustomerid
                    FROM tcasino.T_Customer;

                    v_nonamecustomerid := COALESCE(v_nonamecustomerid, 0) + 1;

                    INSERT INTO tcasino.T_Customer (CustomerId, Firstname, Lastname)
                    VALUES (v_nonamecustomerid, 'NONAME', v_nonamecustomerid::TEXT);

                    PERFORM tcasino.tsp_createcustomerfields(v_nonamecustomerid);
                END;
            END IF;

            SELECT CardNo
            INTO v_nonamecardno
            FROM tcasino.T_Card
            WHERE CustomerId = v_nonamecustomerid AND MachineInsertedDate IS NULL
            ORDER BY CardId
            LIMIT 1;

            v_nonamecardno := COALESCE(v_nonamecardno, '');

            IF LENGTH(v_nonamecardno) = 0 THEN
                BEGIN
                    v_nonamecardno := EXTRACT(EPOCH FROM (NOW() - '2019-01-01 00:00:00'::TIMESTAMP))::TEXT;
                    INSERT INTO tcasino.T_Card(CustomerId, CardNo, IsActive)
                    VALUES(v_nonamecustomerid, v_nonamecardno, TRUE)
                    RETURNING CardId INTO v_cardid;
                END;
            END IF;

            p_cardno := v_nonamecardno;
        END;
    END IF;

    CREATE TEMPORARY TABLE tempcustomer ON COMMIT DROP AS
    SELECT
        t.*,
        pc.IsActive AS IsCustomerActive,
        pc.Firstname || ' ' || pc.Lastname AS Fullname,
        pc.Firstname,
        pc.Firstname AS Nickname,
        tca.BonusConstant * COALESCE(cc.SlotBonusPercentage, 0.0015) * 1000 AS BonusPercentage,
        tcasino.fn_getexchangedamount(COALESCE(pc.CurrentBonus, 0), v_casinocurrencyid, v_machinecurrencyid) AS CurrentBonus,
        pc.Gender,
        tca.TotalTrueIn,
        tca.TotalVisitCount,
        pc.TrackingCode,
        tca.CanPlayMultipleCard
    FROM tcasino.T_Card t
    INNER JOIN tcasino.T_Customer pc ON pc.CustomerId = t.CustomerId
    LEFT JOIN tcasino.T_CustomerAdditional tca ON tca.CustomerId = pc.CustomerId
    LEFT JOIN tcasino.T_CustomerClass cc ON cc.ClassId = pc.CustomerClassId
    WHERE t.CardNo = p_cardno;

    RAISE NOTICE '@CardNo%', p_cardno;

    SELECT CardId INTO v_cardid FROM tempcustomer LIMIT 1;

    BEGIN
        SELECT CustomerId, IsCustomerActive, IsActive, TrackingCode
        INTO v_customerid, v_iscustomeractive, v_iscardactive, v_trackingcode
        FROM tempcustomer;
    EXCEPTION
        WHEN OTHERS THEN
            NULL; -- Suppress the notice
    END;
    v_customerid := COALESCE(v_customerid, 0);
    v_trackingcode := COALESCE(v_trackingcode, '');

    BEGIN
        SELECT CanPlayMultipleCard INTO v_canplaymultiplecard FROM tempcustomer;
        v_iscardhasselfbalance := v_canplaymultiplecard;
    EXCEPTION
        WHEN OTHERS THEN
            NULL; -- Suppress the notice
    END;

    RAISE NOTICE 'visits';

    BEGIN
        SELECT Fullname INTO v_customerfullname FROM tempcustomer;
    EXCEPTION
        WHEN OTHERS THEN
            NULL; -- Suppress the notice
    END;

    v_result := 1;
    v_errormessage := '';
    SELECT CurrentMacAddress, MachineInsertedDate
    INTO v_lmacaddress, v_lenterdate
    FROM tcasino.T_Card
    WHERE CardNo = p_cardno;

    IF v_cashinlimit > 0 THEN
        v_moneylimit := v_cashinlimit;
    END IF;

    SELECT CardType
    INTO v_cardtype
    FROM tcasino.T_Card
    WHERE CardNo = p_cardno;
    v_cardtype := COALESCE(v_cardtype, 0);

    IF v_cardtype = 2 THEN
        v_moneylimit := 500;
    END IF;

    IF v_iscashless = 0 THEN
        v_moneylimit := 0;
    END IF;

    IF p_deviceid = 0 THEN
        BEGIN
            v_result := 0;
            v_errormessage := 'There is no such machine with this MacAddress';
            INSERT INTO tcasino.T_ImportantMessages(MacAddress, Message, MessageType)
            VALUES(p_macaddress, v_errormessage, 1);
        END;
    END IF;

    -- Blacklist check (variables moved to main DECLARE)
    SELECT IsRouletteBlackList, IsSlotBlackList
    INTO v_isrouletteblacklist, v_isslotblacklist
    FROM tcasino.T_CustomerAdditional
    WHERE CustomerId = v_customerid;

    v_isrouletteblacklist := COALESCE(v_isrouletteblacklist, FALSE);
    v_isslotblacklist := COALESCE(v_isslotblacklist, FALSE);

    IF (v_isslotblacklist = TRUE AND v_machinetype = 0) OR (v_isrouletteblacklist = TRUE AND v_machinetype = 1) THEN
        BEGIN
            v_result := 0;
            v_errormessage := 'PLAYER IS ON NO GAME LIST!';
            INSERT INTO tcasino.T_ImportantMessages(MacAddress, Message, MessageType, CustomerId)
            VALUES(p_macaddress, v_errormessage, 1, v_customerid);
        END;
    END IF;

    -- Last Used Date (variables moved to main DECLARE)
    SELECT LastUsedDate INTO v_lastuseddate FROM tcasino.T_Card WHERE CardNo = p_cardno;
    v_lastuseddate := COALESCE(v_lastuseddate, NOW() - INTERVAL '1 year');

    v_lastusedsecdiff := EXTRACT(EPOCH FROM (NOW() - v_lastuseddate))::BIGINT;

    IF v_lastusedsecdiff >= 0 AND v_lastusedsecdiff < 5 THEN
        BEGIN
            v_result := 0;
            v_errormessage := 'Please wait for 5 secs for new card!';
        END;
    END IF;

    IF v_result <> 0 THEN
        UPDATE tcasino.T_Card SET LastUsedDate = NOW() WHERE CardNo = p_cardno;
    END IF;
    -- End Last Used Date

    v_uploadmoney := 1;
    SELECT MachineLogId, ExitDate, CardNo
    INTO v_tempmachinelogid, v_tempexitdate, v_tempcardno
    FROM tcasino.T_CardMachineLogs
    WHERE MacAddress = p_macaddress
    ORDER BY MachineLogId DESC
    LIMIT 1;

    IF v_tempmachinelogid IS NOT NULL AND v_tempexitdate IS NULL THEN
        BEGIN
            IF v_tempcardno = p_cardno THEN
                BEGIN
                    IF v_result = 1 THEN
                        v_uploadmoney := 0;
                        v_result := 1;
                        v_errormessage := 'Settings.ini error! But we fixed it!';
                    END IF;
                    NULL; -- Removed RAISE NOTICE '';
                END;
            ELSE
                BEGIN
                    v_result := 0;
                    v_errormessage := 'GM is already in use. First Control! @NewCardNo:' || v_tempcardno || ' @CardNo:' || p_cardno;
                END;
            END IF;
            INSERT INTO tcasino.T_ImportantMessages(MacAddress, Message, MessageType)
            VALUES(p_macaddress, v_errormessage, 100);
        END;
    END IF;

    IF (SELECT COUNT(*) FROM tcasino.T_CardMachineLogs WHERE GamingDate = v_gamingday AND CardNo = p_cardno AND ExitDate IS NULL AND DeviceId <> p_deviceid) > 0 THEN
        BEGIN
            v_result := 0;
            v_errormessage := 'Card is not free';
        END;
    END IF;

    IF v_lmacaddress <> p_macaddress AND LENGTH(v_lmacaddress) > 1 AND v_result = 1 THEN
        BEGIN
            v_result := 0;
            SELECT MachineName INTO v_errormessage FROM tcasino.T_Device WHERE MacAddress = v_lmacaddress;
            v_errormessage := p_cardno || ' is already inserted on ' || COALESCE(v_errormessage, '');
        END;
    END IF;

    IF v_customerid = 0 THEN
        BEGIN
            v_result := 0;
            v_errormessage := 'Customer has no card';
        END;
    ELSE
        PERFORM tcasino.tsp_createcustomerfields(v_customerid);
    END IF;

    v_probidedamount := 0;
    v_probidedamountpromoin := 0;
    IF v_iscardhasselfbalance = FALSE THEN
        SELECT SUM(InputBalance), SUM(PromoIn)
        INTO v_probidedamount, v_probidedamountpromoin
        FROM tcasino.T_CardMachineLogs t
        WHERE CardNo <> p_cardno
            AND LENGTH(CardNo) > 0
            AND ExitDate IS NULL
            AND CardNo IN (SELECT CardNo FROM tcasino.T_Card WHERE CustomerId = v_customerid);
    END IF;
    v_probidedamount := COALESCE(v_probidedamount, 0);
    v_probidedamountpromoin := COALESCE(v_probidedamountpromoin, 0);
    v_probidedamount := 0; -- These two lines seem to reset the values immediately after calculating them.
    v_probidedamountpromoin := 0; -- Double-check if this is the intended logic.

    SELECT AccountId INTO v_accountid FROM tcasino.T_Account WHERE CustomerId = v_customerid;

    BEGIN
        PERFORM tcasino.tsp_calcaccountbalance(v_accountid, v_cardid);
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'TEST ERR';
    END;

    SELECT Balance, PromoBalance
    INTO v_balance, v_promobalance
    FROM tcasino.T_CardBalances
    WHERE CustomerId = v_customerid AND CardId = v_cardid
    LIMIT 1;

    v_balance := FLOOR(COALESCE(v_balance, 0));
    v_promobalance := FLOOR(COALESCE(v_promobalance, 0));

    v_balance := FLOOR(v_balance / 1) * 1;
    v_promobalance := FLOOR(v_promobalance / 1) * 1;

    IF v_balance >= p_customcashable AND p_customcashable > 0 THEN
        v_balance := p_customcashable;
    END IF;

    RAISE NOTICE 'Card balance%', v_balance;

    v_balance := COALESCE(v_balance, 0);
    IF v_balance < 0 THEN
        v_balance := 0;
    END IF;

    IF v_promobalance < 0 THEN
        v_promobalance := 0;
    END IF;

    IF v_promobalance < 0 THEN
        v_promobalance := 0;
    END IF;

    IF v_probidedamount > 0 OR v_probidedamountpromoin > 0 THEN
        BEGIN
            v_normalbalance := v_balance;
            RAISE NOTICE 'Probided';
            v_balance := v_balance - v_probidedamount;
            v_promobalance := 0;

            v_normalpromobalance := v_promobalance;
            IF v_probidedamountpromoin > 0 THEN
                v_promobalance := COALESCE(v_promobalance, 0) - v_probidedamountpromoin;
            END IF;

            v_errormessage := p_cardno || ' There is already game playing to this customer. Blocked Amount: ' || v_probidedamount::TEXT || ' Normal Amount:' || v_normalbalance::TEXT || ' Blocked Promo: ' || v_probidedamountpromoin::TEXT || ' Normal Promo:' || v_normalpromobalance::TEXT;

            INSERT INTO tcasino.T_ImportantMessages(MacAddress, Message, MessageType)
            VALUES(p_macaddress, v_errormessage, 29);
        END;
    END IF;

    IF v_balance > v_moneylimit THEN
        BEGIN
            RAISE NOTICE 'money limit';
            v_balance := v_moneylimit;
        END;
    END IF;

    IF v_promobalance > v_moneylimit THEN
        v_promobalance := v_moneylimit;
    END IF;

    IF v_promobalance > 0 AND v_ispromoaccepts = FALSE THEN
        v_promobalance := 0;
    END IF;

    IF v_iscustomeractive = FALSE AND v_result = 1 THEN
        BEGIN
            v_result := 0;
            v_errormessage := 'Customer is not active! ' || p_cardno;
        END;
    END IF;

    IF v_iscardactive = FALSE AND v_result = 1 THEN
        BEGIN
            v_result := 0;
            v_errormessage := 'Card is not active! ' || p_cardno;

            BEGIN
                v_messageimportant := v_customerfullname || '''s Disactive card is inserted!|' || p_cardno;

                IF (SELECT COUNT(*) FROM tcasino.T_ImportantMessages WHERE WarningType = 23 AND Message = v_messageimportant AND (CreatedDate + INTERVAL '3 minute') > NOW()) = 0 THEN
                    INSERT INTO tcasino.T_ImportantMessages(MacAddress, MessageType, Message, CreatedDate, WarningType)
                    VALUES(p_macaddress, 0, v_messageimportant, NOW(), 23);

                    BEGIN
                        INSERT INTO tcasino.T_CustomerImportantMessages(CustomerId, CardNo, DeviceId, MachineLogId, MessageType, Message, CreatedDate)
                        VALUES(v_customerid, p_cardno, p_deviceid, 0, 'DisactiveCardInsert', v_messageimportant, NOW());
                    EXCEPTION
                        WHEN OTHERS THEN
                            RAISE NOTICE 'Insert Customer Important Messages';
                    END;
                END IF;
            EXCEPTION
                WHEN OTHERS THEN
                    NULL; -- Suppress the notice
            END;
        END;
    END IF;

    IF v_iscashless = 0 THEN
        BEGIN
            RAISE NOTICE 'Not cashless';
            v_balance := 0;
            v_promobalance := 0;
        END;
    END IF;

    v_balance := tcasino.fn_getamountwithoutcent(v_balance);
    v_promobalance := tcasino.fn_getamountwithoutcent(v_promobalance);

    v_cardmachinelogid := 0;
    IF v_result = 1 AND v_uploadmoney = 1 THEN
        BEGIN
            UPDATE tcasino.T_Card SET CurrentMacAddress = p_macaddress, MachineInsertedDate = NOW(), ModifiedDate = NOW() WHERE CardNo = p_cardno;

            v_currentbalance := COALESCE(v_balance, 0) + COALESCE(v_promobalance, 0);

            UPDATE tcasino.T_CustomerAdditional SET LastOperationDate = NOW(), LastGamingDate = v_gamingday, CurrentMachineBalance = v_currentbalance WHERE CustomerId = v_customerid;

            INSERT INTO tcasino.T_CardMachineLogs
            (DeviceId, GamingDate, CageDate, MacAddress, CardNo, EnterDate, ExitDate, InputBalance, OutputBalance, PromoIn, PromoOut, CurrentBalance, CurrentPromo)
            VALUES
            (p_deviceid, v_gamingday, v_gamingday, p_macaddress, p_cardno, NOW(), NULL, v_balance, 0, v_promobalance, 0, v_currentbalance, v_promobalance)
            RETURNING MachineLogId INTO v_cardmachinelogid;

            BEGIN
                INSERT INTO tcasino.T_CardMachineTransactions(MachineLogId, Amount, PromoAmount, TransactionType, IsCompleted, CreatedDate)
                VALUES(v_cardmachinelogid, v_balance, v_promobalance, 1, TRUE, NOW());
            EXCEPTION
                WHEN OTHERS THEN
                    NULL; -- Suppress the notice
            END;
        END;
    END IF;
    v_cardmachinelogid := COALESCE(v_cardmachinelogid, 0);

    BEGIN
        DELETE FROM tcasino.T_ActiveSessions WHERE DeviceId = p_deviceid;
        INSERT INTO tcasino.T_ActiveSessions
        (MachineLogId, DeviceId, GamingDate, MacAddress, CardNo, EnterDate, ExitDate, InputBalance, OutputBalance, PromoIn, PromoOut, CurrentBalance, CurrentPromo)
        VALUES
        (v_cardmachinelogid, p_deviceid, v_gamingday, p_macaddress, p_cardno, NOW(), NULL, v_balance, 0, v_promobalance, 0, v_currentbalance, v_promobalance);
    EXCEPTION
        WHEN OTHERS THEN
            NULL; -- Suppress the notice
    END;

    IF v_uploadmoney = 0 THEN
        v_cardmachinelogid := v_tempmachinelogid;
    END IF;

    -- Cage Campaign
    IF v_result = 1 THEN
        BEGIN
            SELECT CageCampaignSaleId, CageCampaignId
            INTO v_cagecampaignsaleid, v_cagecampaignid
            FROM tcasino.T_CageCampaignSales
            WHERE CardNo = p_cardno AND IsCompleted = FALSE
            ORDER BY CageCampaignSaleId DESC
            LIMIT 1;

            v_cagecampaignsaleid := COALESCE(v_cagecampaignsaleid, 0);

            IF v_cagecampaignsaleid > 0 THEN
                BEGIN
                    v_keepbillacceptorclosed := 1;

                    UPDATE tcasino.T_CageCampaignSales SET LastMachineLogId = v_cardmachinelogid, LastGamingDate = v_gamingday WHERE CageCampaignSaleId = v_cagecampaignsaleid;
                    INSERT INTO tcasino.T_CageCampaignSaleMachineLogs(CageCampaignSaleId, CardMachineLogId) VALUES(v_cagecampaignsaleid, v_cardmachinelogid);

                    SELECT IsCloseBillAcceptor INTO v_keepbillacceptorclosed FROM tcasino.T_CageCampaigns WHERE CageCampaignId = v_cagecampaignid;
                    v_keepbillacceptorclosed := COALESCE(v_keepbillacceptorclosed, 0);
                END;
            END IF;
        EXCEPTION
            WHEN OTHERS THEN
                NULL; -- Suppress the notice
        END;
    END IF;
    -- End Cage Campaign

    RETURN QUERY
    SELECT
        v_result AS Result,
        v_errormessage AS ErrorMessage,
        v_cardmachinelogid AS CardMachineLogId,
        v_iscashless AS IsCashless,
        p_deviceid AS DeviceId,
        p_nonamerequest AS IsNoname,
        c.CardId,
        c.CardNo,
        c.CustomerId,
        c.CreatedDate,
        c.CreatedBy,
        c.ModifiedDate,
        c.IsActive,
        c.CardType,
        c.DedicatedAmount,
        c.DedicatedPromo,
        c.IsCustomerActive,
        c.Fullname,
        c.Firstname,
        c.Nickname,
        c.BonusPercentage,
        c.CurrentBonus,
        c.Gender,
        c.TotalTrueIn,
        c.TotalVisitCount,
        c.TrackingCode,
        c.CanPlayMultipleCard,
        v_balance AS Balance,
        v_promobalance AS PromoBalance,
        v_uploadmoney AS UploadMoney,
        v_keepbillacceptorclosed AS KeepBillAcceptorClosed,
        v_showwarningtime AS ShowWarningTime,
        v_showwarningheader AS ShowWarningHeader,
        v_showwarningtext AS ShowWarningText
    FROM tempcustomer c;

    IF v_result = 1 THEN
        BEGIN
            UPDATE tcasino.T_Card SET LastUsedDate = NOW() WHERE CardNo = p_cardno;
            UPDATE tcasino.T_Device SET IsInUse = TRUE, CurrentMoney = v_balance, MachineLogId = v_cardmachinelogid, LastOperationDate = NOW() WHERE DeviceId = p_deviceid;
            UPDATE tcasino.T_Customer SET CardMachineLogId = v_cardmachinelogid WHERE CustomerId = v_customerid;

            BEGIN
                IF LENGTH(v_trackingcode) > 0 THEN
                    INSERT INTO tcasino.T_ImportantMessages(MacAddress, MessageType, Message, CreatedDate, WarningType)
                    VALUES(p_macaddress, 0, v_customerfullname || ' => ' || v_balance::TEXT || ' IN Code:' || v_trackingcode, NOW(), 31);
                END IF;
            EXCEPTION
                WHEN OTHERS THEN
                    NULL; -- Suppress the notice
            END;
        END;
    END IF;

    BEGIN
        PERFORM tcasino.tsp_calccustomerbankbalance(v_customerid);
    EXCEPTION
        WHEN OTHERS THEN
            NULL; -- Suppress the notice
    END;

    INSERT INTO tcasino.T_CardReadExitHistory(MacAddress, CardNo, Result, ErrorMessage)
    VALUES(p_macaddress, p_cardno, v_result, v_errormessage);

END;
$BODY$;



-------------------------------------

-- FUNCTION: tcasino.tsp_cardreadpartial(text, text)

-- DROP FUNCTION IF EXISTS tcasino.tsp_cardreadpartial(text, text);

CREATE OR REPLACE FUNCTION tcasino.tsp_cardreadpartial(
    p_macaddress text DEFAULT 'A0E12DE0'::text,
    p_cardno text DEFAULT 'A0E12DE0'::text)
    RETURNS TABLE(cardtypeid bigint, cardid bigint, cardno text, customerid bigint, createddate timestamp without time zone, createdby bigint, modifieddate timestamp without time zone, isactive boolean, cardtype bigint, dedicatedamount numeric, dedicatedpromo numeric, currentmacaddress text, machineinserteddate timestamp without time zone, lastuseddate timestamp without time zone, pincode text, pincodeattempt bigint, maxpincodeattempttry integer) 
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
    ROWS 1000

AS $BODY$
BEGIN
    RETURN QUERY
    SELECT
        COALESCE(t.CardType, 0) AS CardTypeId,
        t.CardId,
        t.CardNo,
        t.CustomerId,
        t.CreatedDate,
        t.CreatedBy,
        t.ModifiedDate,
        t.IsActive,
        t.CardType,
        t.DedicatedAmount,
        t.DedicatedPromo,
        t.CurrentMacAddress,
        t.MachineInsertedDate,
        t.LastUsedDate,
        cua.PinCode,
        COALESCE(cua.PinCodeAttempt, 0) AS PinCodeAttempt,
        3 AS MaxPinCodeAttemptTry
    FROM tcasino.T_Card t
    INNER JOIN tcasino.T_CustomerAdditional cua ON cua.CustomerId = t.CustomerId
    WHERE t.CardNo = p_cardno AND t.IsActive = TRUE;
END;
$BODY$;

----------------------------
-- FUNCTION: tcasino.tsp_cardreadaddmoney(bigint, bigint, numeric, bigint, numeric)

-- DROP FUNCTION IF EXISTS tcasino.tsp_cardreadaddmoney(bigint, bigint, numeric, bigint, numeric);

CREATE OR REPLACE FUNCTION tcasino.tsp_cardreadaddmoney(
    p_machinelogid bigint DEFAULT 1723890,
    p_customerid bigint DEFAULT 1414,
    p_amount numeric DEFAULT 151,
    p_operationtype bigint DEFAULT 1,
    p_currentbalance numeric DEFAULT 0)
    RETURNS TABLE(result bigint, errormessage text, operationtype bigint, amount numeric, balance numeric, probidedamount numeric, probidedamountpromoin numeric) 
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
    ROWS 1000

AS $BODY$
DECLARE
    v_result BIGINT;
    v_errormessage TEXT;
    v_balance NUMERIC;
    v_promobalance NUMERIC;
    v_inputbalance NUMERIC;
    v_cardno TEXT;
    v_deviceid BIGINT;
    v_ispromoaccepts BOOLEAN;
    v_cashinlimit NUMERIC;
    v_iscashless INT;
    v_machinecurrencyid BIGINT;
    v_machinetype INT;
    v_macaddress TEXT;
    v_probidedamount NUMERIC;
    v_probidedamountpromoin NUMERIC;
BEGIN
    v_result := 1;
    v_errormessage := 'Good luck!';

    IF p_amount < 1 THEN
        v_result := -1;
        v_errormessage := 'Amount should be greater than 1';
    END IF;

    SELECT Balance, PromoBalance
    INTO v_balance, v_promobalance
    FROM tcasino.T_Account
    WHERE CustomerId = p_customerid
    LIMIT 1;

    SELECT CardNo, CurrentBalance, DeviceId
    INTO v_cardno, p_currentbalance, v_deviceid
    FROM tcasino.T_CardMachineLogs
    WHERE MachineLogId = p_machinelogid AND ExitDate IS NULL;

    v_cardno := COALESCE(v_cardno, '');
    p_currentbalance := COALESCE(p_currentbalance, 0);

    SELECT
        IsPromoAccepts,
        CashInLimit,
        IsCashless,
        MachineCurrencyId,
        MachineType,
        MacAddress
    INTO
        v_ispromoaccepts,
        v_cashinlimit,
        v_iscashless,
        v_machinecurrencyid,
        v_machinetype,
        v_macaddress
    FROM tcasino.T_Device
    WHERE DeviceId = v_deviceid
    LIMIT 1;

    v_cashinlimit := COALESCE(v_cashinlimit, 0);

    IF p_operationtype = 1 THEN
        IF p_amount > v_cashinlimit THEN
            p_amount := v_cashinlimit;
            v_result := -1;
            v_errormessage := 'Max Limit for Cash In is ' || v_cashinlimit::TEXT;
        END IF;
    END IF;

    IF COALESCE((SELECT COUNT(*) FROM tcasino.T_Card WHERE CardNo = v_cardno AND CustomerId = p_customerid), 0) = 0 THEN
        v_result := -1;
        v_errormessage := 'SessionReload';
    END IF;

    SELECT SUM(InputBalance), SUM(PromoIn)
    INTO v_probidedamount, v_probidedamountpromoin
    FROM tcasino.T_CardMachineLogs t
    WHERE CardNo = v_cardno
        AND LENGTH(v_cardno) > 0
        AND ExitDate IS NULL
        AND CardNo IN (SELECT CardNo FROM tcasino.T_Card WHERE CustomerId = p_customerid);

    v_probidedamount := COALESCE(v_probidedamount, 0);
    v_probidedamountpromoin := COALESCE(v_probidedamountpromoin, 0);

    IF v_balance < (v_probidedamount + p_amount) THEN
        v_result := -1;
        v_errormessage := 'You can add max ' || (v_balance - v_probidedamount)::TEXT || ' Credit!';
    END IF;

    BEGIN
        IF v_probidedamount > 0 THEN
            INSERT INTO tcasino.T_ImportantMessages(MacAddress, MessageType, Message, CreatedDate, WarningType, CustomerId)
            VALUES(v_macaddress, 1, 'Blocked Amount on Account: ' || v_probidedamount::TEXT, NOW(), 0, p_customerid);
        END IF;
    EXCEPTION
        WHEN OTHERS THEN
            NULL; -- Suppress the notice
    END;

    IF p_operationtype = 2 THEN
        UPDATE tcasino.T_CardMachineLogs SET InputBalance = InputBalance + p_amount, CurrentBalance = p_currentbalance WHERE MachineLogId = p_machinelogid;

        INSERT INTO tcasino.T_CardMachineTransactions(MachineLogId, Amount, TransactionType, IsCompleted, CreatedDate)
        VALUES(p_machinelogid, p_amount, 2, TRUE, NOW());
    END IF;

    RETURN QUERY
    SELECT
        v_result AS Result,
        v_errormessage AS ErrorMessage,
        p_operationtype AS OperationType,
        p_amount AS Amount,
        v_balance AS Balance,
        v_probidedamount AS ProbidedAmount,
        v_probidedamountpromoin AS ProbidedAmountPromoIn;

END;
$BODY$;

------------------------------------


-- Create the PostgreSQL procedure
CREATE OR REPLACE FUNCTION tcasino."tsp_cardexit"(
    p_cardmachinelogid    BIGINT,
    p_macaddress          VARCHAR,
    p_cardno              VARCHAR,
    p_balance             NUMERIC(19,4),
    p_playcount           BIGINT,
    p_userid              BIGINT DEFAULT 0,
    p_totalbet            NUMERIC(19,4) DEFAULT 0,
    p_totalwin            NUMERIC(19,4) DEFAULT 0,
    p_promo               NUMERIC(19,4) DEFAULT 0,
    p_isproblemoncredit   INTEGER DEFAULT 0,
    p_machinebonus        VARCHAR DEFAULT '0',
    p_cardexitstatus      INTEGER DEFAULT 0 -- 0: Normal, 1: Balance reset (Handpay drop), 2: Cashout is pressed
)
RETURNS TABLE(result BIGINT, errormessage VARCHAR, errormessagecode BIGINT)
LANGUAGE plpgsql
AS $$
DECLARE
    v_balance NUMERIC(19,4);
    v_promo NUMERIC(19,4);
    v_iscardhasselfbalance BOOLEAN;
    v_casinocurrencyid BIGINT;
    v_errormessagecode BIGINT;
    v_machinetype BIGINT;
    v_isbonusgives BOOLEAN;
    v_deviceid BIGINT;
    v_currentgamingdate DATE;
    v_machinecurrencyid BIGINT;
    v_result BIGINT;
    v_errormessage VARCHAR;
    v_exitdate TIMESTAMP;
    v_cardno VARCHAR;
    v_gamingdate DATE;
    v_tcashableamount NUMERIC(19,4);
    v_cashoutmsg VARCHAR;
    v_devicetypeid BIGINT;
    v_manufacturername VARCHAR;
    v_letmalfunction BOOLEAN;
    v_message VARCHAR;
    v_cashableamount NUMERIC(19,4);
    v_msg1 VARCHAR;
    v_avgbet NUMERIC(19,4);
    v_accountid BIGINT;
    v_customerid BIGINT;
    v_currentbonus NUMERIC(19,4);
    v_totalbonus NUMERIC(19,4);
    v_bonuspercentage NUMERIC(19,4);
    v_earnedbonus NUMERIC(19,4);
    v_billacceptoramount NUMERIC(19,4);
    v_jackpotwons NUMERIC(19,4);
    v_casinopromotype INTEGER;
    v_inputbalance NUMERIC(19,4);
    v_promoin NUMERIC(19,4);
    v_totalcash NUMERIC(19,4);
    v_cagedate DATE;
    v_fark NUMERIC(19,4);
    v_farkpromo NUMERIC(19,4);
    v_iscashless INTEGER;
    v_farklocal NUMERIC(19,4);
    v_farkpromolocal NUMERIC(19,4);
    v_cardid BIGINT;
    v_isfark BOOLEAN;
BEGIN
    -- Initialize variables
    v_balance := p_balance;
    v_promo := p_promo;
    v_errormessagecode := 0;
    v_result := 1;
    v_avgbet := 0;
    v_letmalfunction := TRUE;
    v_earnedbonus := 0;
    v_casinopromotype := 0;
    v_iscashless := 1;
    v_isfark := FALSE;
    
    -- Validate balance and promo
    IF v_balance < 0 THEN
        v_balance := 0;
    END IF;
    
    IF v_promo < 0 THEN
        v_promo := 0;
    END IF;
    
    -- Get casino settings
    SELECT iscardhasselfbalance, currencyid 
    INTO v_iscardhasselfbalance, v_casinocurrencyid 
    FROM t_casinosettings 
    LIMIT 1;
    
    -- Get device information
    SELECT deviceid INTO v_deviceid 
    FROM t_cardmachinelogs 
    WHERE machinelogid = p_cardmachinelogid;
    
    SELECT isbonusgives, machinetype, deviceid, currentgamingdate, machinecurrencyid 
    INTO v_isbonusgives, v_machinetype, v_deviceid, v_currentgamingdate, v_machinecurrencyid 
    FROM t_device 
    WHERE deviceid = v_deviceid 
    LIMIT 1;
    
    -- Get exit information
    SELECT exitdate, cardno, gamingdate 
    INTO v_exitdate, v_cardno, v_gamingdate 
    FROM t_cardmachinelogs 
    WHERE machinelogid = p_cardmachinelogid;
    
    -- Check if already processed
    IF v_exitdate IS NOT NULL THEN
        BEGIN
            IF (SELECT COUNT(*) FROM t_accounttransactions 
                WHERE sourcetype = 1 AND sourceid = p_cardmachinelogid) > 0 THEN
                
                v_result := -1;
                v_errormessage := 'Card exit process is already done';
                v_errormessagecode := -1;
                
            ELSE
                INSERT INTO t_importantmessages(macaddress, messagetype, message, createddate, warningtype)
                VALUES (p_macaddress, 1, 'Let exit process again!', NOW(), 0);
            END IF;
        EXCEPTION 
            WHEN OTHERS THEN
                NULL;
        END;
    END IF;
    
    IF v_result > 0 THEN
        -- Update card machine logs
        UPDATE t_cardmachinelogs 
        SET exitdate = NOW(), billacceptoramount = 0 
        WHERE machinelogid = p_cardmachinelogid;
        
        -- Update device
        UPDATE t_device 
        SET currentmoney = 0, session_lastbet = 0 
        WHERE deviceid = v_deviceid;
        
        -- Update card
        UPDATE t_card 
        SET lastuseddate = NOW() 
        WHERE cardno = p_cardno;
        
        -- Check cashable amount
        BEGIN
            IF p_playcount > 0 AND v_balance = 0 THEN
                SELECT cashableamount INTO v_tcashableamount 
                FROM t_devicemoneyquery 
                WHERE cardno = p_cardno AND macaddress = p_macaddress 
                ORDER BY deviceanswerid DESC 
                LIMIT 1;
                
                v_tcashableamount := COALESCE(v_tcashableamount, 0);
                
                IF v_tcashableamount <> v_balance THEN
                    v_cashoutmsg := 'Slot malfunction!- Amount:0, Real Amount! ' || 
                                   v_tcashableamount::VARCHAR || ' CardNo: ' || p_cardno;
                    
                    PERFORM tsp_insimportantmessage(p_macaddress, v_cashoutmsg, 30);
                END IF;
            END IF;
        EXCEPTION 
            WHEN OTHERS THEN
                NULL;
        END;
        
        -- Get device type information
        SELECT devicetypeid, manufacturername 
        INTO v_devicetypeid, v_manufacturername 
        FROM t_device 
        WHERE macaddress = p_macaddress;
        
        -- Check malfunction conditions
        IF p_isproblemoncredit = 0 THEN
            v_letmalfunction := FALSE;
        END IF;
        
        IF p_cardexitstatus = 2 THEN
            v_letmalfunction := FALSE;
        END IF;
        
        -- Handle malfunction scenario
        IF ((p_isproblemoncredit = 1 AND p_playcount = 0) OR 
            (p_playcount = 0 AND v_balance = 0 AND v_promo = 0)) AND v_letmalfunction THEN
            
            SELECT inputbalance, COALESCE(promoin, 0) 
            INTO v_balance, v_promo 
            FROM t_cardmachinelogs 
            WHERE machinelogid = p_cardmachinelogid;
            
            IF v_balance > 0 OR v_promo > 0 THEN
                v_message := 'Money was going to be removed by abnormal activity, it has been prevented C:' || 
                            p_cardno || ' L:' || p_cardmachinelogid::VARCHAR;
                
                PERFORM tsp_insimportantmessage(p_macaddress, v_message, 30);
            END IF;
        END IF;
        
        -- Check balance consistency
        BEGIN
            IF p_playcount > 0 AND 2 = 3 THEN -- This condition will never be true (2=3)
                SELECT cashableamount INTO v_cashableamount 
                FROM t_devicemoneyquery 
                WHERE macaddress = p_macaddress 
                ORDER BY deviceanswerid DESC 
                LIMIT 1;
                
                v_cashableamount := COALESCE(v_cashableamount, 0);
                
                IF v_cashableamount <> v_balance THEN
                    v_msg1 := 'Last money query and current balance is not the same: C:' || 
                             p_cardno || ' L:' || p_cardmachinelogid::VARCHAR || 
                             ' B:' || v_balance::VARCHAR || ' CashQuery:' || v_cashableamount::VARCHAR;
                    
                    PERFORM tsp_insimportantmessage(p_macaddress, v_msg1, 30);
                END IF;
            END IF;
        EXCEPTION 
            WHEN OTHERS THEN
                NULL;
        END;
        
        -- Handle balance reset
        IF p_cardexitstatus = 1 THEN
            v_balance := 0;
            v_promo := 0;
        END IF;
        
        -- Update device status
        UPDATE t_device 
        SET isinuse = FALSE, currentmoney = 0, machinelogid = 0 
        WHERE deviceid = v_deviceid;
        
        -- Get customer and account information
        SELECT a.accountid, t.customerid, c.currentbonus, c.totalbonus, 
               COALESCE(cc.slotbonuspercentage, c.bonuspercentage)
        INTO v_accountid, v_customerid, v_currentbonus, v_totalbonus, v_bonuspercentage
        FROM t_card t
        INNER JOIN t_customer c ON c.customerid = t.customerid
        INNER JOIN t_account a ON a.customerid = t.customerid
        LEFT JOIN t_customerclass cc ON cc.classid = c.customerclassid
        WHERE t.cardno = p_cardno
        LIMIT 1;
        
        -- Calculate earned bonus
        v_earnedbonus := p_totalbet * v_bonuspercentage;
        v_earnedbonus := COALESCE(v_earnedbonus, 0);
        v_earnedbonus := 0; -- Bonus is disabled
        
        IF NOT v_isbonusgives THEN
            v_earnedbonus := 0;
        ELSE
            BEGIN
                v_earnedbonus := p_machinebonus::NUMERIC;
            EXCEPTION 
                WHEN OTHERS THEN
                    v_earnedbonus := 0;
            END;
            
            v_earnedbonus := COALESCE(v_earnedbonus, 0);
            -- Apply currency conversion if needed (assuming function exists)
            -- v_earnedbonus := fn_getexchangedamount(v_earnedbonus, v_machinecurrencyid, v_casinocurrencyid);
        END IF;
        
        v_currentbonus := v_currentbonus + v_earnedbonus;
        v_totalbonus := v_totalbonus + v_earnedbonus;
        
        -- Get bill acceptor amount
        SELECT COALESCE(SUM(amount), 0) INTO v_billacceptoramount 
        FROM t_devicebillacceptor 
        WHERE machinelogid = p_cardmachinelogid;
        
        -- Get jackpot wins
        BEGIN
            SELECT COALESCE(SUM(a.wonamount), 0) INTO v_jackpotwons
            FROM t_jackpotwons a
            INNER JOIN t_jackpotlevels l ON l.jackpotlevelid = a.jackpotlevelid AND l.islockneeded = TRUE
            WHERE a.machinelogid = p_cardmachinelogid;
        EXCEPTION 
            WHEN OTHERS THEN
                v_jackpotwons := 0;
        END;
        
        -- Handle casino promo type
        IF v_casinopromotype = 1 THEN
            SELECT inputbalance, promoin 
            INTO v_inputbalance, v_promoin 
            FROM t_cardmachinelogs 
            WHERE machinelogid = p_cardmachinelogid;
            
            v_inputbalance := COALESCE(v_inputbalance, 0);
            v_promoin := COALESCE(v_promoin, 0);
            
            IF v_promoin > 0 AND (v_inputbalance > 0 OR v_billacceptoramount > 0) THEN
                BEGIN
                    v_totalcash := v_inputbalance + v_billacceptoramount;
                EXCEPTION 
                    WHEN OTHERS THEN
                        NULL;
                END;
            END IF;
        END IF;
        
        -- Get cage date
        BEGIN
            SELECT gamingday INTO v_cagedate 
            FROM t_gamingdays 
            WHERE cagestarteddate IS NOT NULL 
            ORDER BY gamingdayid DESC 
            LIMIT 1;
            
            v_cagedate := COALESCE(v_cagedate, CURRENT_DATE);
        EXCEPTION 
            WHEN OTHERS THEN
                v_cagedate := CURRENT_DATE;
        END;
        
        -- Update card machine logs with final values
        UPDATE t_cardmachinelogs 
        SET jackpotwons = v_jackpotwons,
            billacceptoramount = v_billacceptoramount,
            exitdate = NOW(),
            outputbalance = v_balance,
            playcount = p_playcount,
            userid = p_userid,
            totalbet = p_totalbet,
            totalwin = p_totalwin,
            earnedbonus = COALESCE(earnedbonus, 0) + v_earnedbonus,
            avgbet = v_avgbet,
            promoout = v_promo,
            cagedate = v_cagedate
        WHERE machinelogid = p_cardmachinelogid;
        
        -- Update customer
        UPDATE t_customer 
        SET cardmachinelogid = 0, currentbonus = v_currentbonus, totalbonus = v_totalbonus 
        WHERE customerid = v_customerid;
        
        UPDATE t_customeradditional 
        SET lastoperationdate = NOW() + INTERVAL '1 minute', currentmachinebalance = 0 
        WHERE customerid = v_customerid;
        
        -- Update card
        UPDATE t_card 
        SET currentmacaddress = '', machineinserteddate = NULL 
        WHERE cardno = p_cardno;
        
        -- Calculate differences
        SELECT COALESCE(outputbalance, 0) - COALESCE(inputbalance, 0),
               promoout - promoin, promoin 
        INTO v_fark, v_farkpromo, v_promoin 
        FROM t_cardmachinelogs 
        WHERE machinelogid = p_cardmachinelogid;
        
        v_fark := COALESCE(v_fark, 0);
        v_farkpromo := COALESCE(v_farkpromo, 0);
        
        -- Insert transaction record
        BEGIN
            INSERT INTO t_cardmachinetransactions(machinelogid, amount, promoamount, transactiontype, iscompleted, createddate)
            VALUES (p_cardmachinelogid, v_balance, v_promo, 3, TRUE, NOW());
        EXCEPTION 
            WHEN OTHERS THEN
                NULL;
        END;
        
        -- Get cashless setting
        SELECT iscashless INTO v_iscashless 
        FROM t_device 
        WHERE macaddress = p_macaddress 
        LIMIT 1;
        
        v_iscashless := COALESCE(v_iscashless, 1);
        
        -- Handle currency conversion
        v_farklocal := v_fark;
        v_farkpromolocal := v_farkpromo;
        
        -- Apply currency conversion if needed (assuming function exists)
        -- v_fark := fn_getexchangedamount(v_fark, v_machinecurrencyid, v_casinocurrencyid);
        -- v_farkpromo := fn_getexchangedamount(v_farkpromo, v_machinecurrencyid, v_casinocurrencyid);
        
        -- Get card ID
        SELECT cardid INTO v_cardid 
        FROM t_card 
        WHERE cardno = p_cardno;
        
        -- Handle account transactions
        IF v_fark <> 0 AND v_iscashless = 1 THEN
            v_isfark := TRUE;
            PERFORM tsp_insaccounttransaction(
                v_accountid, 1, v_fark, 1, p_cardmachinelogid, 
                v_farklocal, v_machinecurrencyid, v_cardid
            );
        END IF;
        
        IF v_farkpromo <> 0 AND v_iscashless = 1 THEN
            v_isfark := TRUE;
            PERFORM tsp_insaccounttransaction(
                v_accountid, 6, v_farkpromo, 1, p_cardmachinelogid,
                v_farkpromolocal, v_machinecurrencyid, v_cardid
            );
        END IF;
        
        -- Calculate account balance if no difference
        IF NOT v_isfark THEN
            BEGIN
                PERFORM tsp_calcaccountbalance(v_accountid, v_cardid);
            EXCEPTION 
                WHEN OTHERS THEN
                    NULL;
            END;
        END IF;
        
    END IF; -- End of if v_result > 0
    
    -- Return results
    RETURN QUERY SELECT v_result, v_errormessage, v_errormessagecode;
    
    -- Handle failed card exit
    IF v_errormessagecode = -1 THEN
        PERFORM tsp_failedcardexit(p_cardmachinelogid, 2);
    END IF;
    
    -- Clean up active sessions
    BEGIN
        DELETE FROM t_activesessions WHERE machinelogid = p_cardmachinelogid;
    EXCEPTION 
        WHEN OTHERS THEN
            NULL;
    END;
    
    -- Calculate customer bank balance
    BEGIN
        PERFORM tsp_calccustomerbankbalance(v_customerid);
    EXCEPTION 
        WHEN OTHERS THEN
            NULL;
    END;
    
    -- Calculate device daily result if gaming date changed
    BEGIN
        IF v_currentgamingdate <> v_gamingdate THEN
            PERFORM job_calcdevicedailyresult(v_deviceid, v_gamingdate);
        END IF;
    EXCEPTION 
        WHEN OTHERS THEN
            NULL;
    END;
    
END;
$$;


------------------------------------------

-- FUNCTION: tcasino.tsp_insgamestart(text, bigint, money, money, money, text, integer, bigint, money, bigint, bigint, bigint, bigint, bigint, money)

-- DROP FUNCTION IF EXISTS tcasino.tsp_insgamestart(text, bigint, money, money, money, text, integer, bigint, money, bigint, bigint, bigint, bigint, bigint, money);

CREATE OR REPLACE FUNCTION tcasino.tsp_insgamestart(
    p_macaddress text,
    p_machinelogid bigint,
    p_wagered money,
    p_wonamount money DEFAULT 0,
    p_totalcoinin money DEFAULT NULL::money,
    p_wager_type text DEFAULT NULL::text,
    p_progressivegroup integer DEFAULT NULL::integer,
    p_selectedgameid bigint DEFAULT NULL::bigint,
    p_usedpromo money DEFAULT 0,
    p_deviceid bigint DEFAULT 0,
    p_totalplaycount bigint DEFAULT 0,
    p_gender bigint DEFAULT 0,
    p_customerid bigint DEFAULT 0,
    p_devicetypegroupid bigint DEFAULT 0,
    p_totalcoininmeter money DEFAULT 0,
    OUT result bigint,
    OUT errormessage text,
    OUT jwid bigint,
    OUT levelname text,
    OUT islockneeded boolean)
    RETURNS record
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
AS $BODY$
#variable_conflict use_column
DECLARE
    v_wagered_local MONEY := p_wagered;
    v_totalcoinin_local MONEY := p_totalcoinin;
    v_totalplaycount_local BIGINT := p_totalplaycount;
    v_gamestartid BIGINT;
    v_jackpotwonid BIGINT;
    v_jackpotid BIGINT;
    v_jackpotfactor MONEY;
    v_casinowonamount MONEY;
    v_affectedrows BIGINT;
    v_activesessioncount BIGINT;
    v_avgbet MONEY; -- Retained as is, assuming it might be assigned from a function/calculation that could return null or a value.
    v_jl_levelname TEXT;
    v_jl_islockneeded BOOLEAN;
BEGIN
    IF v_wagered_local < 0 THEN
        v_wagered_local := 0;
    END IF;

    IF v_wagered_local > 10000 THEN
        v_wagered_local := 0;
    END IF;

    BEGIN
        UPDATE tcasino.T_DeviceGameInfo 
        SET TotalGamePlayed = COALESCE(TotalGamePlayed, 0) + 1, 
            TotalCoinIn = TotalCoinIn + v_wagered_local
        WHERE DeviceId = p_deviceid AND GameId = p_selectedgameid;

        GET DIAGNOSTICS v_affectedrows = ROW_COUNT;
        v_affectedrows := COALESCE(v_affectedrows, 0);

        IF v_affectedrows = 0 THEN
            INSERT INTO tcasino.T_DeviceGameInfo(
                DeviceId, GameId, TotalCoinIn, TotalGamePlayed
            )
            VALUES (
                p_deviceid, p_selectedgameid, p_totalcoininmeter, 1
            );
        END IF;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'Error updating/inserting T_DeviceGameInfo: %', SQLERRM;
    END;

    IF EXTRACT(SECOND FROM NOW()) % 3 = 0 THEN
        UPDATE tcasino.T_Device 
        SET Session_LastBet = v_wagered_local, 
            LastOperationDate = NOW() 
        WHERE MacAddress = p_macaddress;
    END IF;

    INSERT INTO tcasino.T_GameStarts (
        MachineLogId, Wagered, UsedPromo, TotalCoinIn, WagerType, 
        ProgressiveGroup, SelectedGameId
    )
    VALUES (
        p_machinelogid, v_wagered_local, p_usedpromo, v_totalcoinin_local, p_wager_type, 
        p_progressivegroup, p_selectedgameid
    )
    RETURNING GameStartId INTO v_gamestartid;

    --<Jackpot>-------------------
    SELECT td.JackpotId, td.JackpotFactor
    INTO v_jackpotid, v_jackpotfactor
    FROM tcasino.T_Device td 
    WHERE td.MacAddress = p_macaddress;
    
    v_jackpotid := COALESCE(v_jackpotid, 0);
    v_jackpotfactor := COALESCE(v_jackpotfactor, 1);
    v_casinowonamount := COALESCE(v_wagered_local, 0) - COALESCE(p_usedpromo, 0);

    IF v_jackpotid > 0 AND v_casinowonamount > 0 THEN
        UPDATE tcasino.T_JackpotLevels
        SET CurrentAmount = CurrentAmount + COALESCE(v_jackpotfactor * v_casinowonamount * (SharePercent::NUMERIC(20, 8)), 0),
            HitCount = HitCount + 1
        WHERE JackpotId = v_jackpotid;

        BEGIN
            SELECT COUNT(*) 
            INTO v_activesessioncount 
            FROM tcasino.T_Device 
            WHERE IsInUse = TRUE AND JackpotId = v_jackpotid AND IsOnline = TRUE;
            
            v_activesessioncount := COALESCE(v_activesessioncount, 0);
            v_totalcoinin_local := COALESCE(v_totalcoinin_local, 0);
            v_totalplaycount_local := COALESCE(v_totalplaycount_local, 0);

            -- Ensure v_avgbet is initialized or calculated if it's used without prior assignment
            -- For now, assuming p_wagered (v_wagered_local) is the intended avgbet if not otherwise set
            v_avgbet := v_wagered_local; 

            PERFORM tcasino.tsp_JackpotWinTry(
                p_jackpotid := v_jackpotid,
                p_gamestartid := v_gamestartid,
                p_activesessioncount := v_activesessioncount,
                p_currentbet := v_wagered_local,
                p_avgbet := v_avgbet, -- Using the explicitly set v_avgbet
                p_totalwager := v_totalcoinin_local,
                p_totalplaycount := v_totalplaycount_local,
                p_machinelogid := p_machinelogid,
                p_gender := p_gender,
                p_customerid := p_customerid,
                p_devicetypegroupid := p_devicetypegroupid,
                p_jackpotwonid := v_jackpotwonid, -- This is an OUT parameter in the called function
                p_jackpotfactor := v_jackpotfactor
            );
        EXCEPTION
            WHEN OTHERS THEN
                RAISE NOTICE 'Error during tsp_JackpotWinTry: %', SQLERRM;
        END;
    END IF;
    --<Jackpot>-------------------

    SELECT
        jw.LevelName,
        jl.IsLockNeeded
    INTO
        v_jl_levelname,
        v_jl_islockneeded
    FROM tcasino.T_JackpotWons jw
    LEFT JOIN tcasino.T_JackpotLevels jl ON jl.JackpotLevelId = jw.JackpotLevelId
    WHERE jw.JackpotWonId = v_jackpotwonid;

    Result := v_gamestartid;
    ErrorMessage := '';
    JWId := COALESCE(v_jackpotwonid, 0);
    LevelName := v_jl_levelname;
    IsLockNeeded := COALESCE(v_jl_islockneeded, FALSE);
    RETURN;
END;
$BODY$;

-----------------------------------------
-- FUNCTION: tcasino.tsp_insgameend(text, bigint, money, bigint, bigint, money, bigint, money, money, money)

-- DROP FUNCTION IF EXISTS tcasino.tsp_insgameend(text, bigint, money, bigint, bigint, money, bigint, money, money, money);

CREATE OR REPLACE FUNCTION tcasino.tsp_insgameend(
    p_macaddress text,
    p_machinelogid bigint,
    p_winamount money,
    p_selectedgameid bigint,
    p_gamestartid bigint,
    p_currentbalance money DEFAULT '-1'::integer,
    p_deviceid bigint DEFAULT 0,
    p_currentpromo money DEFAULT 0,
    p_wagered money DEFAULT 0,
    p_notifywonlimit money DEFAULT 1000,
    OUT result integer,
    OUT errormessage text,
    OUT jwid integer)
    RETURNS record
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
AS $BODY$
#variable_conflict use_column
DECLARE
    v_currentbalance_local MONEY := p_currentbalance;
    v_currentpromo_local MONEY := p_currentpromo;
    v_wagered_local MONEY := p_wagered;
    v_gamestartid_local BIGINT := p_gamestartid;
BEGIN
    IF v_currentbalance_local < 0 THEN
        v_currentbalance_local := 0;
    END IF;

    IF v_currentpromo_local < 0 THEN
        v_currentpromo_local := 0;
    END IF;

    BEGIN
        IF p_winamount >= p_notifywonlimit THEN
            IF v_wagered_local = 0 THEN
                SELECT Wagered INTO v_wagered_local 
                FROM tcasino.T_GameStarts 
                WHERE GameStartId = v_gamestartid_local;
            END IF;

            INSERT INTO tcasino.T_GameBigWons (
                GameStartId, SelectedGameId, MacAddress, MachineLogId, WinAmount, CurrentBalance,
                DeviceId, CurrentPromo, CreatedDate, Wagered
            )
            VALUES (
                v_gamestartid_local, p_selectedgameid, p_macaddress, p_machinelogid, p_winamount, v_currentbalance_local,
                p_deviceid, v_currentpromo_local, NOW(), v_wagered_local
            );
        END IF;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'Error inserting into T_GameBigWons: %', SQLERRM;
    END;

    IF v_currentbalance_local = -999 THEN
        UPDATE tcasino.T_CardMachineLogs 
        SET AvgBet = p_winamount 
        WHERE MachineLogId = p_machinelogid;
        
        SELECT CurrentBalance INTO v_currentbalance_local 
        FROM tcasino.T_CardMachineLogs 
        WHERE MachineLogId = p_machinelogid;
        
        v_currentbalance_local := v_currentbalance_local + p_winamount;
    END IF;

    IF v_gamestartid_local = 0 THEN
        SELECT MAX(GameStartId) INTO v_gamestartid_local 
        FROM tcasino.T_GameStarts 
        WHERE MachineLogId = p_machinelogid AND EndDate IS NULL;
    END IF;

    UPDATE tcasino.T_GameStarts 
    SET WonAmount = p_winamount, EndDate = NOW(), CurrentBalance = v_currentbalance_local 
    WHERE GameStartId = v_gamestartid_local;

    IF EXTRACT(SECOND FROM NOW()) % 5 = 0 OR v_gamestartid_local % 5 = 0 THEN
        UPDATE tcasino.T_Device 
        SET CurrentMoney = v_currentbalance_local 
        WHERE MacAddress = p_macaddress;
        
        UPDATE tcasino.T_CardMachineLogs 
        SET CurrentBalance = v_currentbalance_local, CurrentPromo = v_currentpromo_local, AvgBet = v_wagered_local 
        WHERE MachineLogId = p_machinelogid;
        
        UPDATE tcasino.T_CustomerAdditional 
        SET CurrentMachineBalance = v_currentbalance_local 
        WHERE CardMachineLogId = p_machinelogid;
    END IF;

    BEGIN
        UPDATE tcasino.T_ActiveSessions 
        SET CurrentBalance = v_currentbalance_local, CurrentPromo = v_currentpromo_local, AvgBet = v_wagered_local 
        WHERE MachineLogId = p_machinelogid;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'Error updating T_ActiveSessions: %', SQLERRM;
    END;

    Result := 1;
    ErrorMessage := '';
    JWId := 0;
    RETURN;
END;
$BODY$;
----------------------------------------------------

-- Create the PostgreSQL procedure
CREATE OR REPLACE FUNCTION tcasino."tsp_insgamestartend"(
    p_macaddress           VARCHAR,
    p_machinelogid         BIGINT,
    p_wagered              NUMERIC(19,4),
    p_totalcoinin          NUMERIC(19,4),
    p_wagertype            VARCHAR,
    p_progressivegroup     INTEGER,
    p_selectedgameid       BIGINT,
    p_usedpromo            NUMERIC(19,4) DEFAULT 0,
    p_deviceid             BIGINT DEFAULT 0,
    p_totalplaycount       BIGINT DEFAULT 0,
    p_gender               BIGINT DEFAULT 0,
    p_customerid           BIGINT DEFAULT 0,
    p_devicetypegroupid    BIGINT DEFAULT 0,
    p_totalcoininmeter     NUMERIC(19,4) DEFAULT 0,
    -- Game End parameters
    p_winamount            NUMERIC(19,4) DEFAULT 0,
    p_gamestartid          BIGINT DEFAULT 0,
    p_currentbalance       NUMERIC(19,4) DEFAULT -1,
    p_currentpromo         NUMERIC(19,4) DEFAULT 0,
    p_notifywonlimit       NUMERIC(19,4) DEFAULT 1000,
    p_jackpotid            BIGINT DEFAULT 0,
    p_jackpotfactor        NUMERIC(19,4) DEFAULT 0,
    p_machinecurrencyid    BIGINT DEFAULT 0,
    p_casinocurrencyid     BIGINT DEFAULT 0
)
RETURNS TABLE(
    result BIGINT,
    errormessage VARCHAR,
    jwid BIGINT,
    jackpotwonid BIGINT,
    jackpotlevelid BIGINT,
    deviceid BIGINT,
    winamount NUMERIC,
    levelname VARCHAR,
    islockneeded INTEGER,
    wonamountlocal NUMERIC
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_wagered NUMERIC(19,4);
    v_currentbalance NUMERIC(19,4);
    v_currentpromo NUMERIC(19,4);
    v_affectedrows BIGINT;
    v_gamewon BIGINT;
    v_gamestartid BIGINT;
    v_jackpotwonid BIGINT;
    v_casinowonamt NUMERIC(19,4);
    v_activesessioncount BIGINT;
    v_avgbet NUMERIC(19,4);
    v_triggeredjackpotwonid BIGINT;
    v_count INTEGER;
BEGIN
    -- Initialize variables
    v_wagered := p_wagered;
    v_currentbalance := p_currentbalance;
    v_currentpromo := p_currentpromo;
    v_gamestartid := p_gamestartid;
    v_jackpotwonid := 0;
    v_affectedrows := 0;
    v_gamewon := 0;
    
    -- Validate wagered amount
    IF v_wagered < 0 THEN
        v_wagered := 0;
    END IF;
    
    IF v_wagered > 6000 AND p_selectedgameid <> 1 THEN
        v_wagered := 1;
    END IF;
    
    -- Update T_DeviceGameInfo
    BEGIN
        UPDATE t_devicegameinfo 
        SET totalgameplayed = COALESCE(totalgameplayed, 0) + 1,
            totalcoinin = totalcoinin + v_wagered,
            totalcoinout = totalcoinout + p_winamount
        WHERE deviceid = p_deviceid AND gameid = p_selectedgameid;
        
        GET DIAGNOSTICS v_affectedrows = ROW_COUNT;
        v_affectedrows := COALESCE(v_affectedrows, 0);
        
        IF v_affectedrows = 0 AND p_selectedgameid > 0 THEN
            INSERT INTO t_devicegameinfo(deviceid, gameid, totalcoinin, totalgameplayed, totalcoinout)
            VALUES (p_deviceid, p_selectedgameid, p_totalcoininmeter, 1, p_winamount);
        END IF;
    EXCEPTION 
        WHEN OTHERS THEN
            NULL;
    END;
    
    -- Update T_DeviceGameInfoByWager
    BEGIN
        IF p_winamount > 0 THEN
            v_gamewon := 1;
        END IF;
        
        v_affectedrows := 0;
        
        UPDATE t_devicegameinfobywager
        SET totalgameplayed = totalgameplayed + 1,
            totalgamewon = totalgamewon + v_gamewon,
            totalcoinin = totalcoinin + v_wagered,
            totalcoinout = totalcoinout + p_winamount,
            lastwager = NOW()
        WHERE deviceid = p_deviceid AND gameid = p_selectedgameid AND wager = v_wagered;
        
        GET DIAGNOSTICS v_affectedrows = ROW_COUNT;
        v_affectedrows := COALESCE(v_affectedrows, 0);
        
        IF v_affectedrows = 0 AND p_selectedgameid > 0 THEN
            INSERT INTO t_devicegameinfobywager(
                deviceid, gameid, wager, totalcoinin, totalcoinout, 
                totalgameplayed, totalgamewon, firstwager, lastwager
            )
            VALUES (
                p_deviceid, p_selectedgameid, v_wagered, v_wagered, p_winamount,
                1, v_gamewon, NOW(), NOW()
            );
        END IF;
        
        -- Debug output (equivalent to print statement)
        RAISE NOTICE '%s %s %s %s', p_deviceid, p_selectedgameid, v_affectedrows, v_wagered;
        
    EXCEPTION 
        WHEN OTHERS THEN
            RAISE NOTICE 'Error On t_devicegameinfobywager';
    END;
    
    -- Validate current balance and promo
    IF v_currentbalance < 0 THEN
        v_currentbalance := 0;
    END IF;
    
    IF v_currentpromo < 0 THEN
        v_currentpromo := 0;
    END IF;
    
    -- Insert game start record
    INSERT INTO t_gamestarts(
        machinelogid, wagered, usedpromo, selectedgameid, wonamount, 
        enddate, currentbalance, wagertype
    )
    VALUES (
        p_machinelogid, v_wagered, p_usedpromo, p_selectedgameid, p_winamount,
        NOW(), v_currentbalance, p_wagertype
    )
    RETURNING gamestartid INTO v_gamestartid;
    
    -- Handle big wins
    BEGIN
        IF p_winamount >= p_notifywonlimit THEN
            IF v_wagered = 0 THEN
                SELECT wagered INTO v_wagered 
                FROM t_gamestarts 
                WHERE gamestartid = v_gamestartid 
                LIMIT 1;
            END IF;
            
            INSERT INTO t_gamebigwons(
                gamestartid, selectedgameid, macaddress, machinelogid,
                winamount, currentbalance, deviceid, currentpromo,
                createddate, wagered
            )
            VALUES (
                v_gamestartid, p_selectedgameid, p_macaddress, p_machinelogid,
                p_winamount, v_currentbalance, p_deviceid, v_currentpromo,
                NOW(), v_wagered
            );
        END IF;
    EXCEPTION 
        WHEN OTHERS THEN
            NULL;
    END;
    
    -- Update device status (condition 1=1 always true)
    IF TRUE OR EXTRACT(SECOND FROM NOW())::INTEGER % 2 = 0 OR v_gamestartid % 5 = 0 THEN
        UPDATE t_device 
        SET session_lastbet = v_wagered,
            lastoperationdate = NOW(),
            currentmoney = v_currentbalance 
        WHERE deviceid = p_deviceid;
    END IF;
    
    -- Update card machine logs and customer additional
    IF TRUE OR EXTRACT(SECOND FROM NOW())::INTEGER % 2 = 0 OR v_gamestartid % 10 = 0 OR v_wagered > 15 THEN
        UPDATE t_cardmachinelogs
        SET currentbalance = v_currentbalance,
            currentpromo = v_currentpromo,
            avgbet = v_wagered,
            playcount = p_totalplaycount,
            totalbet = COALESCE(totalbet, 0) + v_wagered,
            totalwin = COALESCE(totalwin, 0) + p_winamount
        WHERE machinelogid = p_machinelogid;
        
        UPDATE t_customeradditional 
        SET currentmachinebalance = v_currentbalance 
        WHERE cardmachinelogid = p_machinelogid;
    END IF;
    
    -- Update active sessions
    BEGIN
        UPDATE t_activesessions
        SET currentbalance = v_currentbalance,
            currentpromo = v_currentpromo,
            avgbet = v_wagered,
            playcount = p_totalplaycount,
            totalbet = COALESCE(totalbet, 0) + v_wagered,
            totalwin = COALESCE(totalwin, 0) + p_winamount
        WHERE machinelogid = p_machinelogid;
    EXCEPTION 
        WHEN OTHERS THEN
            NULL;
    END;
    
    -- Handle jackpot processing
    v_jackpotwonid := COALESCE(p_jackpotid, 0);
    v_casinowonamt := COALESCE(v_wagered, 0) - COALESCE(p_usedpromo, 0);
    
    IF p_jackpotid > 0 AND v_casinowonamt > 0 THEN
        -- Update jackpot levels
        UPDATE t_jackpotlevels 
        SET currentamount = currentamount + COALESCE(p_jackpotfactor * v_casinowonamt * (sharepercent::DECIMAL(20,8)), 0),
            hitcount = hitcount + 1,
            hiddenamount = hiddenamount + COALESCE(p_jackpotfactor * v_casinowonamt * (hiddensharepercent::DECIMAL(20,8)), 0)
        WHERE jackpotid = p_jackpotid;
        
        UPDATE t_jackpotlevels 
        SET sharedcurrentamount = sharedcurrentamount + COALESCE(p_jackpotfactor * v_casinowonamt * (sharedpercentage::DECIMAL(20,8)), 0)
        WHERE sharedpercentage > 0;
        
        -- Process jackpot win attempt
        BEGIN
            SELECT COUNT(*) INTO v_activesessioncount 
            FROM t_device 
            WHERE isinuse = TRUE AND jackpotid = p_jackpotid AND isonline = TRUE;
            
            v_avgbet := v_wagered;
            v_activesessioncount := COALESCE(v_activesessioncount, 0);
            
            RAISE NOTICE '6.';
            
            SELECT * INTO v_jackpotwonid 
            FROM tsp_jackpotwintry(
                p_jackpotid, v_gamestartid, v_activesessioncount, v_wagered, v_wagered,
                p_totalcoinin, p_totalplaycount, p_machinelogid, p_gender, p_customerid,
                p_devicetypegroupid, p_jackpotfactor, p_deviceid
            );
            
        EXCEPTION 
            WHEN OTHERS THEN
                RAISE NOTICE 'pinar ne oldu??';
        END;
    END IF;
    
    -- Handle shared/triggered jackpot
    v_jackpotwonid := COALESCE(v_jackpotwonid, 0);
    
    SELECT jackpotwonid INTO v_triggeredjackpotwonid 
    FROM t_jackpottriggered 
    WHERE deviceid = p_deviceid 
      AND EXTRACT(EPOCH FROM (NOW() - createddate)) < 60 
      AND processeddate IS NULL 
    LIMIT 1;
    
    v_triggeredjackpotwonid := COALESCE(v_triggeredjackpotwonid, 0);
    
    IF v_triggeredjackpotwonid > 0 AND v_jackpotwonid = 0 THEN
        UPDATE t_jackpottriggered 
        SET processeddate = NOW() 
        WHERE jackpotwonid = v_triggeredjackpotwonid AND deviceid = p_deviceid;
        
        DELETE FROM t_jackpottriggered WHERE deviceid = p_deviceid;
        v_jackpotwonid := v_triggeredjackpotwonid;
    END IF;
    
    RAISE NOTICE 'Set Jackpot Won Id : %s', COALESCE(v_jackpotwonid, 0);
    
    -- Return results with jackpot information
    RETURN QUERY
    SELECT 
        v_gamestartid as result,
        ''::VARCHAR as errormessage,
        COALESCE(v_jackpotwonid, 0) as jwid,
        COALESCE(jw.jackpotwonid, 0) as jackpotwonid,
        COALESCE(jw.jackpotlevelid, 0) as jackpotlevelid,
        COALESCE(jw.deviceid, 0) as deviceid,
        COALESCE(jw.wonamount, 0) as winamount,
        COALESCE(jl.levelname, '') as levelname,
        COALESCE(jl.islockneeded::INTEGER, 0) as islockneeded,
        CASE 
            WHEN v_jackpotwonid > 0 THEN 
                -- fn_getexchangedamount equivalent (assuming 1:1 conversion for now)
                COALESCE(jw.wonamount, 0)
            ELSE 0 
        END as wonamountlocal
    FROM (SELECT 1) x  -- Dummy table for cross join
    LEFT JOIN t_jackpotwons jw ON jw.jackpotwonid = v_jackpotwonid
    LEFT JOIN t_jackpotlevels jl ON jl.jackpotlevelid = jw.jackpotlevelid;
    
END;
$$;


-----------------------------------------------

-- PROCEDURE: tcasino.tsp_deldevicegameinfo(bigint)

-- DROP PROCEDURE IF EXISTS tcasino.tsp_deldevicegameinfo(bigint);

CREATE OR REPLACE PROCEDURE tcasino.tsp_deldevicegameinfo(
    IN p_deviceid bigint)
LANGUAGE 'plpgsql'
AS $BODY$
BEGIN
    DELETE FROM T_DeviceGameInfo WHERE DeviceId = p_DeviceId;
    SELECT 1 AS Result, '' AS ErrorMessage;
END;
$BODY$;



-------------------------------------------

-- PROCEDURE: tcasino.tsp_devicestatu(text, integer, text, bigint, bigint, bigint, text, text, text, integer, bigint, bigint, numeric, bigint, text, bigint, boolean, bigint, bigint, bigint, numeric, numeric, numeric, numeric, numeric, numeric)

-- DROP PROCEDURE IF EXISTS tcasino.tsp_devicestatu(text, integer, text, bigint, bigint, bigint, text, text, text, integer, bigint, bigint, numeric, bigint, text, bigint, boolean, bigint, bigint, bigint, numeric, numeric, numeric, numeric, numeric, numeric);

CREATE OR REPLACE PROCEDURE tcasino.tsp_devicestatu(
    IN p_macaddress text,
    IN p_messagetype integer,
    IN p_ipaddress text,
    IN p_versionid bigint DEFAULT 0,
    IN p_issasport bigint DEFAULT 0,
    IN p_iscardreader bigint DEFAULT 0,
    IN p_sasport text DEFAULT ''::text,
    IN p_cardreaderport text DEFAULT ''::text,
    IN p_statutext text DEFAULT ''::text,
    IN p_islocked integer DEFAULT 0,
    IN p_deviceid bigint DEFAULT 0,
    IN p_playcount bigint DEFAULT 0,
    IN p_totalbet numeric DEFAULT 0,
    IN p_machinelogid bigint DEFAULT 0,
    IN p_activescreen text DEFAULT ''::text,
    IN p_onlinecount bigint DEFAULT 0,
    IN p_issaslink boolean DEFAULT false,
    IN p_customerid bigint DEFAULT 0,
    IN p_assetno bigint DEFAULT 0,
    IN p_isbillacceptor bigint DEFAULT 0,
    IN p_wagered numeric DEFAULT 0,
    IN p_currentbalance numeric DEFAULT 0,
    IN p_currentpromo numeric DEFAULT 0,
    IN p_winamount numeric DEFAULT 0,
    IN p_betamount numeric DEFAULT 0,
    IN p_totalwin numeric DEFAULT 0)
LANGUAGE 'plpgsql'
AS $BODY$
DECLARE
    v_DeviceId BIGINT := p_DeviceId; -- Use local variable for modification
    v_IsNewRecord INTEGER := 0;
    v_NewMacAddress TEXT;
    v_GamingDate DATE;
    v_CommandMinuteLeft BIGINT;
BEGIN
    IF (SELECT COUNT(*) FROM T_DeviceIP WHERE AssetNo = p_AssetNo AND IPAddress = p_IPAddress) = 0 THEN
        INSERT INTO T_DeviceIP(IPAddress, AssetNo, CreatedDate) VALUES (p_IPAddress, p_AssetNo, NOW());
    ELSE
        UPDATE T_DeviceIP SET UpdatedDate = NOW() WHERE IPAddress = p_IPAddress AND AssetNo = p_AssetNo;
    END IF;

    IF p_AssetNo > 1 THEN
        SELECT DeviceId
        INTO v_DeviceId
        FROM T_Device
        WHERE AssetNo = p_AssetNo
        ORDER BY DeviceId ASC
        LIMIT 1;

        v_DeviceId := COALESCE(v_DeviceId, 0);
        RAISE NOTICE 'burada bulduk 1 Dev: %', v_DeviceId;
    END IF;

    IF v_DeviceId = 0 AND p_AssetNo > 0 THEN
        SELECT DeviceId
        INTO v_DeviceId
        FROM T_Device
        WHERE RealMacAddress = p_MacAddress AND AssetNo = p_AssetNo;
        v_DeviceId := COALESCE(v_DeviceId, 0);
        RAISE NOTICE 'burada bulduk 2 Dev: %', v_DeviceId;
    END IF;

    IF v_DeviceId = 0 AND p_AssetNo = 0 THEN
        SELECT DeviceId
        INTO v_DeviceId
        FROM T_Device
        WHERE RealMacAddress = p_MacAddress
        ORDER BY DeviceId DESC
        LIMIT 1;
        v_DeviceId := COALESCE(v_DeviceId, 0);
        RAISE NOTICE 'burada bulduk 3 Dev: %', v_DeviceId;
    END IF;

    IF p_AssetNo > 1 AND v_DeviceId > 0 AND p_OnlineCount % 10 = 0 THEN
        UPDATE T_Device SET RealMacAddress = p_MacAddress WHERE AssetNo = p_AssetNo;
    END IF;

    IF v_DeviceId = 0 AND p_AssetNo = 0 THEN
        SELECT DeviceId
        INTO v_DeviceId
        FROM T_Device
        WHERE RealMacAddress = p_MacAddress
        ORDER BY DeviceId DESC
        LIMIT 1;
        v_DeviceId := COALESCE(v_DeviceId, 0);
        RAISE NOTICE 'burada bulduk 2 Dev: %', v_DeviceId;
    END IF;

    IF v_DeviceId = 0 THEN
        RAISE NOTICE 'NO DEVICE :(';
    END IF;

    SELECT CasinoGamingDate INTO v_GamingDate FROM T_CasinoSettings LIMIT 1;

    IF v_DeviceId = 0 THEN
        v_IsNewRecord := 1;
        RAISE NOTICE 'Hey-1';
        
        v_NewMacAddress := p_AssetNo::TEXT;
        IF p_AssetNo = 0 THEN
            v_NewMacAddress := p_MacAddress;
        END IF;

        IF p_OnlineCount = 0 THEN
            BEGIN
                SELECT COALESCE(MAX(DeviceId), 0) + 1 INTO v_DeviceId FROM T_Device;
                INSERT INTO T_Device(DeviceId, MachineName, MacAddress, RealMacAddress, Statu, FirstLoginDate, IPAddress, AssetNo, MachineNo)
                VALUES (v_DeviceId, v_NewMacAddress, v_NewMacAddress, p_MacAddress, 0, NOW(), p_IPAddress, p_AssetNo, p_AssetNo);
            EXCEPTION
                WHEN OTHERS THEN
                    RAISE NOTICE 'ekleyemedi: %', SQLERRM;
            END;
        END IF;
        RAISE NOTICE 'Hey-2';
    ELSE
        IF p_OnlineCount = 0 AND (p_MessageType = 0 OR p_MessageType = 1) THEN
            BEGIN
                INSERT INTO T_DeviceStarts(DeviceId, CreatedDate, MessageType) VALUES (v_DeviceId, NOW(), p_MessageType);
            EXCEPTION
                WHEN OTHERS THEN
                    RAISE NOTICE 'Error inserting T_DeviceStarts: %', SQLERRM;
            END;
        END IF;
        
        IF p_MessageType = 0 THEN
            UPDATE T_Device SET TotalOnlineCount = 0, LastLoginDate = NOW() WHERE DeviceId = v_DeviceId;
        END IF;
        
        IF p_MessageType = 1 THEN
            UPDATE T_Device
            SET
                LastLoginDate = NOW(),
                TotalLoginCount = TotalLoginCount + 1,
                IPAddress = p_IPAddress,
                VersionId = p_VersionId,
                IsSASPort = p_IsSASPort::BOOLEAN, -- Cast to BOOLEAN
                IsCardReader = p_IsCardReader::BOOLEAN, -- Cast to BOOLEAN
                IsBillAcceptor = p_IsBillAcceptor::BOOLEAN -- Cast to BOOLEAN
            WHERE DeviceId = v_DeviceId;
        END IF;
        
        IF p_MessageType = 2 THEN
            UPDATE T_Device
            SET
                TotalOperationCount = TotalOperationCount + 1,
                IPAddress = p_IPAddress,
                VersionId = p_VersionId,
                IsSASPort = p_IsSASPort::BOOLEAN,
                IsCardReader = p_IsCardReader::BOOLEAN,
                IsBillAcceptor = p_IsBillAcceptor::BOOLEAN
            WHERE DeviceId = v_DeviceId;
        END IF;
        
        IF p_MessageType = 3 THEN
            UPDATE T_Device
            SET
                LastOnlineMessage = NOW(),
                TotalOnlineCount = TotalOnlineCount + 1,
                IPAddress = p_IPAddress,
                VersionId = p_VersionId,
                IsSASPort = p_IsSASPort::BOOLEAN,
                IsCardReader = p_IsCardReader::BOOLEAN,
                IsSASLink = p_IsSASLink,
                IsBillAcceptor = p_IsBillAcceptor::BOOLEAN
            WHERE DeviceId = v_DeviceId;

            IF p_MachineLogId > 0 THEN
                BEGIN
                    UPDATE T_CardMachineLogs
                    SET
                        TotalBet = p_TotalBet,
                        PlayCount = p_PlayCount,
                        AvgBet = CASE WHEN p_PlayCount = 0 THEN 0 ELSE p_TotalBet / p_PlayCount END
                    WHERE MachineLogId = p_MachineLogId;
                EXCEPTION
                    WHEN OTHERS THEN
                        RAISE NOTICE 'Error updating T_CardMachineLogs: %', SQLERRM;
                END;
            END IF;
        END IF;
        
        UPDATE T_Device SET IsOnline = TRUE, StatuText = p_StatuText WHERE DeviceId = v_DeviceId;
    END IF;

    IF p_MessageType = 0 THEN
        SELECT
            td.*,
            CAST(td.MachineDenomination / 0.01 AS INTEGER) AS DefBetFactor,
            v_IsNewRecord AS IsNewRecord,
            tss.*,
            cu.CurrencyCode,
            -- FOR XML RAW conversion to a single string separated by '|'
            COALESCE((
                SELECT STRING_AGG(CardNo, '|') FROM T_Card WHERE CardType = 1 AND IsActive = TRUE
            ), '') AS AdminCards,
            COALESCE((
                SELECT STRING_AGG(
                    WagerName || '~' || Wager::TEXT || '~' || BonusFactor::TEXT || '~' || HTMLColour || '~' || WagerNext::TEXT || '~' || StartPercentage::TEXT || '~' || NextPercentage::TEXT, '|'
                ) FROM T_WagerGroups ORDER BY Wager
            ), '') AS WagerBonusFactors,
            NOW() AS ServerDate,
            10 AS CalcBetByTotalCoinInPeriod
        FROM T_Device td
        INNER JOIN T_CasinoSettings tss ON tss.Id = 1
        INNER JOIN T_Currency cu ON cu.CurrencyId = td.MachineCurrencyId
        WHERE td.DeviceId = v_DeviceId;
    END IF;

    IF p_MessageType > 0 THEN
        UPDATE T_Device SET IsLocked = p_IsLocked::BOOLEAN WHERE DeviceId = v_DeviceId;

        v_CommandMinuteLeft := 5;

        -- Union all queries for the result set
        SELECT 'jackpotinfo' AS RowType, ROW_NUMBER() OVER (ORDER BY jl.JackpotLevelId) AS RowNo, '' AS Command, jl.LevelName AS TextInfo, ROUND(jl.CurrentAmount, 2) AS TextValue
        FROM T_Device td
        INNER JOIN T_JackpotLevels jl ON jl.JackpotId = td.JackpotId
        WHERE td.DeviceId = v_DeviceId AND p_ActiveScreen = 'GUI_ShowJackpot'
        
        UNION ALL
        
        SELECT 'cmd' AS RowType, 0 AS RowNo, x.Command, '' AS TextInfo, 0 AS TextValue
        FROM T_DeviceCommands x
        WHERE (x.MacAddress = p_MacAddress OR (p_AssetNo > 0 AND x.MacAddress = p_AssetNo::TEXT))
          AND x.ProcessedDate IS NULL
          AND EXTRACT(EPOCH FROM (NOW() - x.CreatedDate))::BIGINT < (v_CommandMinuteLeft * 60) -- Convert minutes to seconds
        
        UNION ALL
        
        SELECT 'oldgamingdate' AS RowType, 0 AS RowNo, '' AS Command, '' AS TextInfo, 0 AS TextValue
        FROM T_Device td
        WHERE td.CurrentGamingDate <> v_GamingDate AND td.DeviceId = v_DeviceId
        
        UNION ALL
        
        SELECT 'prize' AS RowType, 0 AS RowNo, '' AS Command, p.PrizeDescription AS TextInfo, pw.WonAmount AS TextValue
        FROM T_PrizeWon pw
        INNER JOIN T_Prize p ON p.PrizeId = pw.PrizeId
        WHERE pw.DeviceId = v_DeviceId AND pw.ReceivedDate IS NULL
          AND EXTRACT(EPOCH FROM (NOW() - pw.CreatedDate))::BIGINT < (3 * 60); -- Convert minutes to seconds

        UPDATE T_DeviceCommands
        SET ProcessedDate = NOW()
        WHERE (MacAddress = p_MacAddress OR (p_AssetNo > 0 AND MacAddress = p_AssetNo::TEXT))
          AND ProcessedDate IS NULL
          AND EXTRACT(EPOCH FROM (NOW() - CreatedDate))::BIGINT < (v_CommandMinuteLeft * 60);

        BEGIN
            UPDATE T_PrizeWon
            SET ReceivedDate = NOW()
            WHERE DeviceId = v_DeviceId AND ReceivedDate IS NULL
              AND EXTRACT(EPOCH FROM (NOW() - CreatedDate))::BIGINT < (3 * 60);
        EXCEPTION
            WHEN OTHERS THEN
                RAISE NOTICE 'Error updating T_PrizeWon: %', SQLERRM;
        END;
    END IF;

    -- Using a dummy select to emulate the "endofprocedure" label
    SELECT 1 AS Deneme WHERE FALSE;

END;
$BODY$;


------------------------------------------------


-- Create the PostgreSQL procedure
CREATE OR REPLACE FUNCTION tsp_upddeviceenablesgames(
    p_deviceid         BIGINT,
    p_enabledgameids   VARCHAR,
    p_fullmessage      VARCHAR
)
RETURNS TABLE(result INTEGER, errormessage VARCHAR)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Update all games to inactive for the device
    UPDATE t_devicegameinfo 
    SET isactive = FALSE 
    WHERE deviceid = p_deviceid;
    
    -- Update enabled games to active
    -- Using string_to_array to split comma-separated values and unnest to convert to rows
    UPDATE t_devicegameinfo 
    SET isactive = TRUE 
    WHERE deviceid = p_deviceid
      AND gameid::TEXT = ANY(string_to_array(p_enabledgameids, ','));
    
    -- Return success result
    RETURN QUERY SELECT 1::INTEGER, ''::VARCHAR;
    
END;
$$;


-----------------------------------------------


-- PROCEDURE: tcasino.tsp_getdeviceadditionalinfo(bigint)

-- DROP PROCEDURE IF EXISTS tcasino.tsp_getdeviceadditionalinfo(bigint);

CREATE OR REPLACE PROCEDURE tcasino.tsp_getdeviceadditionalinfo(
    IN p_deviceid bigint)
LANGUAGE 'plpgsql'
AS $BODY$
BEGIN
    SELECT dai.*, dai.IPCameraURL AS RaspberryIPCameraURL 
    FROM T_DeviceAdditionalInfo dai
    WHERE dai.DeviceId = p_DeviceId;
END;
$BODY$;


-------------------------------------------





-- FUNCTION: tcasino.tsp_upddeviceadditionalinfo(bigint, money, text, bigint, bigint, bigint, bigint)

-- DROP FUNCTION IF EXISTS tcasino.tsp_upddeviceadditionalinfo(bigint, money, text, bigint, bigint, bigint, bigint);

CREATE OR REPLACE FUNCTION tcasino.tsp_upddeviceadditionalinfo(
    p_deviceid bigint DEFAULT 1,
    p_temperature money DEFAULT 0,
    p_throttle text DEFAULT ''::text,
    p_threadcount bigint DEFAULT 0,
    p_cpusage bigint DEFAULT 0,
    p_memoryusage bigint DEFAULT 0,
    p_sastimerange bigint DEFAULT 0)
    RETURNS TABLE(result integer, errormessage text) 
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
    ROWS 1000

AS $BODY$
DECLARE
    v_throttle_int INT;
BEGIN
    UPDATE tcasino.T_DeviceAdditionalInfo SET Temperature = p_temperature, SASTimeRange = p_sastimerange WHERE DeviceId = p_deviceid;

    UPDATE tcasino.T_DeviceAdditionalInfo SET CPUUsage = p_cpusage WHERE DeviceId = p_deviceid;
    UPDATE tcasino.T_DeviceAdditionalInfo SET ThreadCount = p_threadcount WHERE DeviceId = p_deviceid;
    UPDATE tcasino.T_DeviceAdditionalInfo SET MemoryUsage = p_memoryusage WHERE DeviceId = p_deviceid;

    BEGIN
        v_throttle_int := p_throttle::INT;
    EXCEPTION WHEN invalid_text_representation THEN
        v_throttle_int := 0; -- Default if conversion fails
    END;

    IF v_throttle_int > 0 THEN
        UPDATE tcasino.T_DeviceAdditionalInfo SET Throttle = p_throttle WHERE DeviceId = p_deviceid;
    END IF;

    Result := 1;
    ErrorMessage := '';
    RETURN NEXT;

END;
$BODY$;

--------------------------------


-- Create the PostgreSQL procedure
CREATE OR REPLACE FUNCTION tcasino."tsp_upddeviceislocked"(
    p_deviceid    BIGINT,
    p_islocked    INTEGER
)
RETURNS TABLE(result INTEGER, errormessage VARCHAR)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Update device lock status
    UPDATE t_device 
    SET islocked = p_islocked 
    WHERE deviceid = p_deviceid;
    
    -- Return success result
    RETURN QUERY SELECT 1::INTEGER, ''::VARCHAR;
    
END;
$$;



----------------------------

-- Create the PostgreSQL procedure
CREATE OR REPLACE FUNCTION tcasino."tsp_updinsertedbalance"(
    p_machinelogid    BIGINT,
    p_inputbalance    NUMERIC(19,4),
    p_promoin         NUMERIC(19,4)
)
RETURNS TABLE(result INTEGER, errormessage VARCHAR)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Update card machine logs with input balance and promo
    UPDATE t_cardmachinelogs
    SET inputbalance = p_inputbalance, 
        promoin = p_promoin
    WHERE machinelogid = p_machinelogid;
    
    -- Return success result
    RETURN QUERY SELECT 1::INTEGER, ''::VARCHAR;
    
END;
$$;

-----------------------------








-- PROCEDURE: tcasino.tsp_getbalanceinfoongm(text, text)

-- DROP PROCEDURE IF EXISTS tcasino.tsp_getbalanceinfoongm(text, text);

CREATE OR REPLACE PROCEDURE tcasino.tsp_getbalanceinfoongm(
    IN p_macaddress text DEFAULT ''::text,
    IN p_cardno text DEFAULT '2C099A7B'::text)
LANGUAGE 'plpgsql'
AS $BODY$
DECLARE
    v_CustomerId BIGINT;
    v_Balance NUMERIC;
    v_PromoBalance NUMERIC;
    v_ProbidedAmount NUMERIC;
    v_ProbidedAmountPromoIn NUMERIC;
BEGIN
    SELECT CustomerId INTO v_CustomerId FROM T_Card WHERE CardNo = p_CardNo;
    
    SELECT Balance, PromoBalance
    INTO v_Balance, v_PromoBalance
    FROM T_Account
    WHERE CustomerId = v_CustomerId
    LIMIT 1;
    v_Balance := COALESCE(v_Balance, 0);
    v_PromoBalance := COALESCE(v_PromoBalance, 0);

    SELECT SUM(InputBalance), SUM(PromoIn)
    INTO v_ProbidedAmount, v_ProbidedAmountPromoIn
    FROM T_CardMachineLogs t
    WHERE LENGTH(CardNo) > 0
      AND ExitDate IS NULL
      AND CardNo IN (SELECT CardNo FROM T_Card WHERE CustomerId = v_CustomerId);
    v_ProbidedAmount := COALESCE(v_ProbidedAmount, 0);
    v_ProbidedAmountPromoIn := COALESCE(v_ProbidedAmountPromoIn, 0);

    SELECT
        v_ProbidedAmount AS ProbidedAmount,
        v_ProbidedAmountPromoIn AS ProbidedAmountPromoIn,
        v_Balance AS Balance,
        v_PromoBalance AS PromoBalance,
        v_Balance - v_ProbidedAmount AS BankBalance;
END;
$BODY$;

-----------------------------------
-- PROCEDURE: tcasino.tsp_getbalanceinfoongm(text, text)

-- DROP PROCEDURE IF EXISTS tcasino.tsp_getbalanceinfoongm(text, text);

CREATE OR REPLACE PROCEDURE tcasino.tsp_getbalanceinfoongm(
    IN p_macaddress text DEFAULT ''::text,
    IN p_cardno text DEFAULT '2C099A7B'::text)
LANGUAGE 'plpgsql'
AS $BODY$
DECLARE
    v_CustomerId BIGINT;
    v_Balance NUMERIC;
    v_PromoBalance NUMERIC;
    v_ProbidedAmount NUMERIC;
    v_ProbidedAmountPromoIn NUMERIC;
BEGIN
    SELECT CustomerId INTO v_CustomerId FROM T_Card WHERE CardNo = p_CardNo;
    
    SELECT Balance, PromoBalance
    INTO v_Balance, v_PromoBalance
    FROM T_Account
    WHERE CustomerId = v_CustomerId
    LIMIT 1;
    v_Balance := COALESCE(v_Balance, 0);
    v_PromoBalance := COALESCE(v_PromoBalance, 0);

    SELECT SUM(InputBalance), SUM(PromoIn)
    INTO v_ProbidedAmount, v_ProbidedAmountPromoIn
    FROM T_CardMachineLogs t
    WHERE LENGTH(CardNo) > 0
      AND ExitDate IS NULL
      AND CardNo IN (SELECT CardNo FROM T_Card WHERE CustomerId = v_CustomerId);
    v_ProbidedAmount := COALESCE(v_ProbidedAmount, 0);
    v_ProbidedAmountPromoIn := COALESCE(v_ProbidedAmountPromoIn, 0);

    SELECT
        v_ProbidedAmount AS ProbidedAmount,
        v_ProbidedAmountPromoIn AS ProbidedAmountPromoIn,
        v_Balance AS Balance,
        v_PromoBalance AS PromoBalance,
        v_Balance - v_ProbidedAmount AS BankBalance;
END;
$BODY$;
----------------------------------------


-- Create the PostgreSQL procedure
CREATE OR REPLACE FUNCTION tcasino."tsp_insimportantmessage"(
    p_macaddress     VARCHAR,
    p_message        VARCHAR,
    p_messagetype    BIGINT,
    p_warningtype    BIGINT DEFAULT 0,
    p_customerid     BIGINT DEFAULT 0
)
RETURNS TABLE(result INTEGER, errormessage VARCHAR)
LANGUAGE plpgsql
AS $$
DECLARE
    v_isdosave BOOLEAN;
    v_warningtype BIGINT;
    v_deviceid BIGINT;
BEGIN
    -- Initialize variables
    v_isdosave := TRUE;
    v_warningtype := p_warningtype;
    
    -- Check specific message conditions
    IF p_message = 'Card reader is not working. Please control card reader' THEN
        v_isdosave := FALSE;
    END IF;
    
    IF p_message LIKE 'Card is not registere%' THEN
        v_warningtype := 0;
    END IF;
    
    IF p_message LIKE 'Bill acceptor hardware failur%' THEN
        v_warningtype := 0;
    END IF;
    
    IF p_message LIKE 'Can''t upload bill acceptor%' THEN
        v_warningtype := 0;
    END IF;
    
    IF p_message LIKE 'Handpay%' AND p_macaddress IN ('290','291','292','293','294','295') THEN
        v_warningtype := 0;
        v_isdosave := TRUE;
    END IF;
    
    IF p_message LIKE 'Cancelled card insert%' THEN
        v_warningtype := 0;
    END IF;
    
    IF p_message LIKE 'Door is opened%' THEN
        v_warningtype := 0;
    END IF;
    
    IF p_message = 'Game is selected: MainScreen' THEN
        v_warningtype := 0;
    END IF;
    
    -- Handle bill rejection
    IF p_message LIKE 'Bill rejecte%' THEN
        SELECT deviceid INTO v_deviceid 
        FROM t_device 
        WHERE macaddress = p_macaddress 
        LIMIT 1;
        
        UPDATE t_deviceadditionalinfo 
        SET billreject = COALESCE(billreject, 0) + 1 
        WHERE deviceid = v_deviceid;
    END IF;
    
    -- Check warning type 5
    IF v_warningtype = 5 THEN
        v_isdosave := FALSE;
    END IF;
    
    -- Insert message if conditions are met
    IF v_isdosave THEN
        INSERT INTO t_importantmessages(macaddress, message, messagetype, warningtype, customerid)
        VALUES (p_macaddress, p_message, p_messagetype, v_warningtype, p_customerid);
    END IF;
    
    -- Return success result
    RETURN QUERY SELECT 1::INTEGER, ''::VARCHAR;
    
END;
$$;


------------------------------------

-- FUNCTION: tcasino.tsp_insexception(text, text, text)

-- DROP FUNCTION IF EXISTS tcasino.tsp_insexception(text, text, text);

CREATE OR REPLACE FUNCTION tcasino.tsp_insexception(
    p_macaddress text,
    p_methodname text,
    p_errormessage text,
    OUT result bigint,
    OUT errormessage text)
    RETURNS record
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
AS $BODY$
#variable_conflict use_column
DECLARE
    v_result BIGINT := 1;
BEGIN
    IF p_macaddress IN ('ClientHelper', 'Online') THEN
        v_result := 0;
    END IF;

    IF v_result > 0 THEN
        INSERT INTO tcasino.T_Exceptions(MacAddress, MethodName, ErrorMessage)
        VALUES(p_macaddress, p_methodname, p_errormessage)
        RETURNING ExceptionId INTO v_result; -- Assuming ExceptionId is the identity column
    END IF;

    Result := v_result;
    ErrorMessage := '';
    RETURN;
END;
$BODY$;

---------------------------------

-- FUNCTION: tcasino.tsp_insdevicedebug(bigint, bigint, text)

-- DROP FUNCTION IF EXISTS tcasino.tsp_insdevicedebug(bigint, bigint, text);

CREATE OR REPLACE FUNCTION tcasino.tsp_insdevicedebug(
    p_machinelogid bigint,
    p_deviceid bigint,
    p_messages text DEFAULT ''::text)
    RETURNS TABLE(result integer, errormessage text) 
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
    ROWS 1000

AS $BODY$
BEGIN
    /* Original was commented out:
    INSERT INTO tcasino.T_DeviceDebug(MachineLogId, DeviceId, CreatedDate, Messages)
    VALUES(p_machinelogid, p_deviceid, NOW(), p_messages);
    */
    Result := 1;
    ErrorMessage := '';
    RETURN NEXT;

END;
$BODY$;

--------------------------------------------------

-- FUNCTION: tcasino.tsp_instracelog(text, text, text, text, bigint)

-- DROP FUNCTION IF EXISTS tcasino.tsp_instracelog(text, text, text, text, bigint);

CREATE OR REPLACE FUNCTION tcasino.tsp_instracelog(
    p_macaddress text,
    p_logtype text,
    p_direction text,
    p_message text,
    p_rowid bigint)
    RETURNS TABLE(result integer, errormessage text) 
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
    ROWS 1000

AS $BODY$
BEGIN
    INSERT INTO tcasino.T_TraceLog(MacAddress, LogType, Direction, Message, CreatedDate, RowId)
    VALUES(p_macaddress, p_logtype, p_direction, p_message, NOW(), p_rowid);

    Result := 1;
    ErrorMessage := '';
    RETURN NEXT;

END;
$BODY$;

------------------------------------------------
-- FUNCTION: tcasino.tsp_instracelog(text, text, text, text, bigint)

-- DROP FUNCTION IF EXISTS tcasino.tsp_instracelog(text, text, text, text, bigint);

CREATE OR REPLACE FUNCTION tcasino.tsp_instracelog(
    p_macaddress text,
    p_logtype text,
    p_direction text,
    p_message text,
    p_rowid bigint)
    RETURNS TABLE(result integer, errormessage text) 
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
    ROWS 1000

AS $BODY$
BEGIN
    INSERT INTO tcasino.T_TraceLog(MacAddress, LogType, Direction, Message, CreatedDate, RowId)
    VALUES(p_macaddress, p_logtype, p_direction, p_message, NOW(), p_rowid);

    Result := 1;
    ErrorMessage := '';
    RETURN NEXT;

END;
$BODY$;
--------------------------------------------------


-- FUNCTION: tcasino.tsp_insreceivedmessage(text, text, integer, text)

-- DROP FUNCTION IF EXISTS tcasino.tsp_insreceivedmessage(text, text, integer, text);

CREATE OR REPLACE FUNCTION tcasino.tsp_insreceivedmessage(
    p_macaddress text,
    p_receivedmessage text,
    p_isprocessed integer,
    p_answercommandname text DEFAULT ''::text)
    RETURNS TABLE(result integer, errormessage text) 
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
    ROWS 1000

AS $BODY$
DECLARE
    v_dosave BOOLEAN := TRUE;
BEGIN
    IF p_receivedmessage LIKE '0172%' THEN
        v_dosave := TRUE;
    END IF;

    IF p_receivedmessage LIKE '0174%' THEN
        v_dosave := TRUE;
    END IF;

    IF p_receivedmessage LIKE '01FF%' THEN
        v_dosave := FALSE;
    END IF;

    IF p_receivedmessage NOT LIKE '01%' THEN
        v_dosave := FALSE;
    END IF;

    IF p_receivedmessage LIKE '01FF69DB5B%' THEN
        v_dosave := FALSE;
    END IF;

    IF LENGTH(p_receivedmessage) < 6 THEN
        v_dosave := FALSE;
    END IF;

    IF p_receivedmessage LIKE '01B3%' THEN
        v_dosave := TRUE;
    END IF;

    IF p_receivedmessage LIKE '01FF7E%' THEN
        v_dosave := TRUE;
    END IF;

    -- EFT
    IF p_receivedmessage LIKE '0128%' OR p_receivedmessage LIKE '0166%' OR p_receivedmessage LIKE '0164%' OR p_receivedmessage LIKE '0169%' THEN
        v_dosave := TRUE;
    END IF;

    IF p_receivedmessage LIKE '012F%' THEN
        v_dosave := TRUE;
    END IF;

    IF v_dosave = TRUE THEN
        INSERT INTO tcasino.T_ReceivedMessages(MacAddress, ReceivedMessage, IsProcessed)
        VALUES(p_macaddress, p_receivedmessage, p_isprocessed);
    END IF;

    Result := 1;
    ErrorMessage := '';
    RETURN NEXT;

END;
$BODY$;
------------------------------------------
-- FUNCTION: tcasino.tsp_insreceivedmessage(text, text, integer, text)

-- DROP FUNCTION IF EXISTS tcasino.tsp_insreceivedmessage(text, text, integer, text);

CREATE OR REPLACE FUNCTION tcasino.tsp_insreceivedmessage(
    p_macaddress text,
    p_receivedmessage text,
    p_isprocessed integer,
    p_answercommandname text DEFAULT ''::text)
    RETURNS TABLE(result integer, errormessage text) 
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
    ROWS 1000

AS $BODY$
DECLARE
    v_dosave BOOLEAN := TRUE;
BEGIN
    IF p_receivedmessage LIKE '0172%' THEN
        v_dosave := TRUE;
    END IF;

    IF p_receivedmessage LIKE '0174%' THEN
        v_dosave := TRUE;
    END IF;

    IF p_receivedmessage LIKE '01FF%' THEN
        v_dosave := FALSE;
    END IF;

    IF p_receivedmessage NOT LIKE '01%' THEN
        v_dosave := FALSE;
    END IF;

    IF p_receivedmessage LIKE '01FF69DB5B%' THEN
        v_dosave := FALSE;
    END IF;

    IF LENGTH(p_receivedmessage) < 6 THEN
        v_dosave := FALSE;
    END IF;

    IF p_receivedmessage LIKE '01B3%' THEN
        v_dosave := TRUE;
    END IF;

    IF p_receivedmessage LIKE '01FF7E%' THEN
        v_dosave := TRUE;
    END IF;

    -- EFT
    IF p_receivedmessage LIKE '0128%' OR p_receivedmessage LIKE '0166%' OR p_receivedmessage LIKE '0164%' OR p_receivedmessage LIKE '0169%' THEN
        v_dosave := TRUE;
    END IF;

    IF p_receivedmessage LIKE '012F%' THEN
        v_dosave := TRUE;
    END IF;

    IF v_dosave = TRUE THEN
        INSERT INTO tcasino.T_ReceivedMessages(MacAddress, ReceivedMessage, IsProcessed)
        VALUES(p_macaddress, p_receivedmessage, p_isprocessed);
    END IF;

    Result := 1;
    ErrorMessage := '';
    RETURN NEXT;

END;
$BODY$;

--------------------------------------------------

-- FUNCTION: tcasino.tsp_inssentcommands(text, bigint, text, text)

-- DROP FUNCTION IF EXISTS tcasino.tsp_inssentcommands(text, bigint, text, text);

CREATE OR REPLACE FUNCTION tcasino.tsp_inssentcommands(
    p_macaddress text,
    p_machinelogid bigint DEFAULT 0,
    p_commandname text DEFAULT NULL::text,
    p_command text DEFAULT NULL::text)
    RETURNS void
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
AS $BODY$
DECLARE
    v_doinsert BOOLEAN := TRUE;
BEGIN
    IF p_command LIKE '01FF7E%' OR p_command LIKE '01FF7F%' THEN
        v_doinsert := FALSE;
    END IF;

    IF p_command LIKE '01FF88%' THEN
        v_doinsert := FALSE;
    END IF;

    IF p_command LIKE '01FF51%' THEN
        v_doinsert := FALSE;
    END IF;

    IF p_command LIKE '01FF1F6A%' THEN
        v_doinsert := FALSE;
    END IF;

    IF p_commandname = 'interragiton' THEN
        v_doinsert := FALSE;
    END IF;

    IF p_commandname = 'MoneyQuery' THEN
        v_doinsert := FALSE;
    END IF;

    IF p_commandname = 'ParaYukle' THEN
        v_doinsert := TRUE;
    END IF;

    IF p_commandname = 'Cashout' THEN
        v_doinsert := TRUE;
    END IF;

    IF p_commandname = 'getmeter2' THEN
        v_doinsert := FALSE;
    END IF;

    IF p_macaddress IN ('B8:27:EB:01:3D:58', 'B8:27:EB:46:7A:32') THEN
        v_doinsert := TRUE;
    END IF;

    IF v_doinsert = TRUE THEN
        INSERT INTO tcasino.T_SentCommands
        (MacAddress, MachineLogId, CommandName, Command)
        VALUES
        (p_macaddress, p_machinelogid, p_commandname, p_command);
    END IF;

END;
$BODY$;

---------------------------
-- PostgreSQL version of sp_InsDeviceWaiterCall
CREATE OR REPLACE FUNCTION tcasino.sp_InsDeviceWaiterCall(
    p_MacAddress VARCHAR,
    p_CustomerId BIGINT
)
RETURNS TABLE(Result INTEGER, ErrorMessage TEXT)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Update the device table with current timestamp
    UPDATE tcasino.T_Device 
    SET BarCallingDate = NOW() 
    WHERE MacAddress = p_MacAddress;
    
    -- Return result set
    RETURN QUERY 
    SELECT 1 AS Result, ''::TEXT AS ErrorMessage;
END;
$$;
--------------------------------------

-- PostgreSQL version of tsp_GetNextVisit
CREATE OR REPLACE FUNCTION tcasino.tsp_GetNextVisit(
    p_DeviceId BIGINT DEFAULT 0,
    p_MachineLogId BIGINT DEFAULT 0,
    p_CardNo VARCHAR DEFAULT NULL,
    p_KioskId BIGINT DEFAULT 1
)
RETURNS TABLE(
    KioskBonusId BIGINT,
    IsWon INTEGER,
    Adet INTEGER,
    Prize INTEGER,
    PrizeType INTEGER
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_Currency VARCHAR;
    v_GamingDate DATE;
    v_Yesterday DATE;
    v_CustomerId BIGINT;
    v_WinLoss NUMERIC(18,2);
    v_KioskBonusId BIGINT;
    v_TodayCageStartedDate TIMESTAMP;
    v_YesterdayCageStartedDate TIMESTAMP;
    v_BonusWonId BIGINT;
    v_Prizes VARCHAR;
    v_PrizeList VARCHAR;
    v_TotalChance BIGINT;
    v_RandomNumber BIGINT;
    v_WonId BIGINT;
    v_Prize NUMERIC(18,2);
    v_Id BIGINT;
    v_ChanceStart BIGINT;
    v_ChanceEnd BIGINT;
    cur CURSOR FOR SELECT id FROM temp_possible_wins;
BEGIN
    -- Get currency from casino settings
    SELECT Currency INTO v_Currency 
    FROM tcasino.T_CasinoSettings 
    LIMIT 1;

    -- Get gaming dates
    SELECT GamingDay, CageStartedDate 
    INTO v_GamingDate, v_TodayCageStartedDate
    FROM tcasino.T_GamingDays 
    ORDER BY GamingDayId DESC 
    LIMIT 1;

    SELECT GamingDay, CageStartedDate 
    INTO v_Yesterday, v_YesterdayCageStartedDate
    FROM tcasino.T_GamingDays 
    WHERE GamingDay < v_GamingDate 
    ORDER BY GamingDayId DESC 
    LIMIT 1;

    -- Get customer ID
    SELECT CustomerId INTO v_CustomerId 
    FROM tcasino.T_Card 
    WHERE CardNo = p_CardNo AND IsActive = 1;

    -- Calculate win/loss
    SELECT COALESCE(SUM(OutputBalance - (InputBalance + COALESCE(BillAcceptorAmount, 0))), 0)
    INTO v_WinLoss
    FROM tcasino.T_CardMachineLogs c
    INNER JOIN tcasino.T_Card tc ON tc.CardNo = c.CardNo
    INNER JOIN tcasino.T_Customer tcc ON tcc.CustomerId = tc.CustomerId AND tcc.CustomerId = v_CustomerId
    WHERE c.CageDate = v_Yesterday AND c.ExitDate IS NOT NULL;

    v_WinLoss := COALESCE(v_WinLoss, 0);

    -- Debug output (PostgreSQL equivalent of PRINT)
    RAISE NOTICE 'Yesterday: %', v_Yesterday;
    RAISE NOTICE 'WinLoss: %', v_WinLoss;

    -- Get kiosk bonus ID based on loss
    SELECT KioskBonusId INTO v_KioskBonusId
    FROM tcasino.T_KioskBonus 
    WHERE ABS(v_WinLoss) >= MinLoss 
    ORDER BY MinLoss DESC 
    LIMIT 1;

    v_KioskBonusId := COALESCE(v_KioskBonusId, 0);

    -- If no loss, no bonus
    IF v_WinLoss >= 0 THEN
        v_KioskBonusId := 0;
        RAISE NOTICE 'No loss occurred yesterday';
    END IF;

    v_WinLoss := ABS(v_WinLoss);

    -- Check if bonus already won today
    SELECT kb.BonusWonId INTO v_BonusWonId
    FROM tcasino.T_Card c
    INNER JOIN tcasino.T_KioskBonusWons kb ON kb.CardNo = c.CardNo
    WHERE kb.GamingDate = tcasino.fn_GetGamingDate(NOW()) AND c.CustomerId = v_CustomerId
    LIMIT 1;

    v_BonusWonId := COALESCE(v_BonusWonId, 0);
    
    IF v_BonusWonId > 0 THEN
        v_KioskBonusId := 0;
        RAISE NOTICE 'Bonus already received today';
    END IF;

    -- Check if cage started today
    IF v_TodayCageStartedDate IS NULL THEN
        v_KioskBonusId := 0;
    END IF;

    -- Get prizes and prize list
    SELECT Prizes, PrizeList INTO v_Prizes, v_PrizeList
    FROM tcasino.T_KioskBonus 
    WHERE KioskBonusId = v_KioskBonusId;

    -- Create temporary table for possible wins
    DROP TABLE IF EXISTS temp_possible_wins;
    
    CREATE TEMP TABLE temp_possible_wins (
        id SERIAL PRIMARY KEY,
        data VARCHAR,
        MinLoss NUMERIC(18,2),
        Factor NUMERIC(18,2),
        Adet NUMERIC(18,2),
        Prize NUMERIC(18,2),
        PrizeType NUMERIC(18,2),
        ChanceStart BIGINT DEFAULT 0,
        ChanceEnd BIGINT DEFAULT 0,
        IsWon INTEGER DEFAULT 0
    );

    -- Split prize list and populate temp table
    INSERT INTO temp_possible_wins (data, MinLoss, Factor, Adet, Prize, PrizeType)
    SELECT 
        value as data,
        CAST(split_part(value, '|', 1) AS NUMERIC(18,2)) as MinLoss,
        CAST(split_part(value, '|', 2) AS NUMERIC(18,2)) as Factor,
        CAST(split_part(value, '|', 3) AS NUMERIC(18,2)) as Adet,
        CASE 
            WHEN CAST(split_part(value, '|', 5) AS NUMERIC(18,2)) > 0 THEN
                CAST(split_part(value, '|', 5) AS NUMERIC(18,2))
            ELSE
                CAST(split_part(value, '|', 4) AS NUMERIC(18,2))
        END as Prize,
        CAST(split_part(value, '|', 5) AS NUMERIC(18,2)) as PrizeType
    FROM unnest(string_to_array(v_PrizeList, ',')) as value
    WHERE LENGTH(TRIM(value)) > 0;

    -- Calculate chance ranges using cursor
    OPEN cur;
    LOOP
        FETCH cur INTO v_Id;
        EXIT WHEN NOT FOUND;

        -- Calculate chance start
        SELECT COALESCE(SUM(CAST(Factor AS BIGINT)), 0) INTO v_ChanceStart
        FROM temp_possible_wins 
        WHERE id < v_Id AND v_WinLoss >= MinLoss;

        -- Calculate chance end
        SELECT COALESCE(SUM(CAST(Factor AS BIGINT)), 0) INTO v_ChanceEnd
        FROM temp_possible_wins 
        WHERE id <= v_Id AND v_WinLoss >= MinLoss;

        IF v_ChanceEnd > 0 THEN
            v_ChanceStart := v_ChanceStart + 1;
        END IF;

        UPDATE temp_possible_wins
        SET ChanceStart = v_ChanceStart, ChanceEnd = v_ChanceEnd
        WHERE id = v_Id;
    END LOOP;
    CLOSE cur;

    -- Get total chance
    SELECT COALESCE(SUM(CAST(Factor AS BIGINT)), 0) INTO v_TotalChance
    FROM temp_possible_wins 
    WHERE v_WinLoss >= MinLoss;

    -- Generate random number
    v_RandomNumber := ROUND(((v_TotalChance - 1) * RANDOM() + 1), 0);

    -- Find winner
    SELECT id, Prize INTO v_WonId, v_Prize
    FROM temp_possible_wins
    WHERE v_RandomNumber BETWEEN ChanceStart AND ChanceEnd
    LIMIT 1;

    v_WonId := COALESCE(v_WonId, 0);
    
    IF v_WonId = 0 THEN
        SELECT MAX(id) INTO v_WonId FROM temp_possible_wins;
    END IF;

    -- Mark winner
    UPDATE temp_possible_wins SET IsWon = 1 WHERE id = v_WonId;

    -- Return results
    RETURN QUERY
    SELECT 
        v_KioskBonusId as KioskBonusId,
        CAST(a.IsWon AS INTEGER) as IsWon,
        CAST(a.Adet AS INTEGER) as Adet,
        CAST(a.Prize AS INTEGER) as Prize,
        CAST(a.PrizeType AS INTEGER) as PrizeType
    FROM temp_possible_wins a
    WHERE Prize > 0 OR PrizeType > 0;

    -- Clean up
    DROP TABLE IF EXISTS temp_possible_wins;
END;
$$;

---------------------------------------------------------

-- PostgreSQL version of tsp_InsProductOrderBySlot
CREATE OR REPLACE FUNCTION tcasino.tsp_InsProductOrderBySlot(
    p_CustomerId BIGINT,
    p_DeviceId BIGINT,
    p_Products VARCHAR
)
RETURNS TABLE(Result BIGINT, ErrorMessage TEXT)
LANGUAGE plpgsql
AS $$
DECLARE
    v_GamingDate DATE;
    v_OrderByType INTEGER := 1;
    v_OrderDate TIMESTAMP := NOW();
    v_IsWaitingApproval BOOLEAN := FALSE;
    v_ApprovedBy INTEGER := 0;
    v_ApprovedDate TIMESTAMP := NOW();
    v_IsWaitingServed BOOLEAN := TRUE;
    v_ServedDate TIMESTAMP := NOW();
    v_DeliveryTypeId BIGINT := 1;
    v_DeliveryLocationId BIGINT;
    v_OrderById BIGINT := 0;
    v_CustomNote TEXT := '';
    v_OrderInfo TEXT := '';
    v_OrderId BIGINT;
BEGIN
    -- Get gaming date
    v_GamingDate := tcasino.fn_GetGamingDate(NOW());
    v_DeliveryLocationId := p_DeviceId;

    -- Insert into T_ProductOrders
    INSERT INTO tcasino.T_ProductOrders (
        GamingDate,
        CustomerId,
        OrderByType,
        OrderById,
        OrderDate,
        IsWaitingApproval,
        ApprovedBy,
        ApprovedDate,
        IsWaitingServed,
        ServedDate,
        CustomNote,
        DeliveryTypeId,
        DeliveryLocationId,
        OrderInfo
    )
    VALUES (
        v_GamingDate,
        p_CustomerId,
        v_OrderByType,
        v_OrderById,
        v_OrderDate,
        v_IsWaitingApproval,
        v_ApprovedBy,
        v_ApprovedDate,
        v_IsWaitingServed,
        v_ServedDate,
        v_CustomNote,
        v_DeliveryTypeId,
        v_DeliveryLocationId,
        v_OrderInfo
    )
    RETURNING OrderId INTO v_OrderId;

    -- Insert order items
    INSERT INTO tcasino.T_ProductOrderItems (OrderId, ProductId, ProductPrice)
    SELECT 
        v_OrderId,
        CAST(split_part(value, ',', 1) AS BIGINT) as ProductId,
        0 as ProductPrice
    FROM unnest(string_to_array(p_Products, '>')) as value
    WHERE LENGTH(TRIM(value)) > 0;

    -- Update total cost and price
    UPDATE tcasino.T_ProductOrders
    SET 
        TotalCost = (
            SELECT COALESCE(SUM(ProductCost), 0) 
            FROM tcasino.T_Products 
            WHERE ProductId IN (
                SELECT ProductId 
                FROM tcasino.T_ProductOrderItems 
                WHERE OrderId = v_OrderId
            )
        ),
        TotalPrice = (
            SELECT COALESCE(SUM(ProductPrice), 0) 
            FROM tcasino.T_Products 
            WHERE ProductId IN (
                SELECT ProductId 
                FROM tcasino.T_ProductOrderItems 
                WHERE OrderId = v_OrderId
            )
        )
    WHERE OrderId = v_OrderId;

    -- Return result
    RETURN QUERY 
    SELECT v_OrderId AS Result, ''::TEXT AS ErrorMessage;

END;
$$;

-----------------------------------------------------

-- PostgreSQL version of tsp_GetProductCategories
CREATE OR REPLACE FUNCTION tcasino.tsp_GetProductCategories()
RETURNS TABLE(
    CategoryId BIGINT,
    CategoryName VARCHAR,
    ParentCategoryId BIGINT,
    IsActive BOOLEAN,
    OrderKey INTEGER,
    CreatedDate TIMESTAMP,
    UpdatedDate TIMESTAMP,
    CreatedBy INTEGER,
    UpdatedBy INTEGER
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT *
    FROM tcasino.T_ProductCategories
    WHERE ParentCategoryId = 0 AND IsActive = TRUE
    ORDER BY OrderKey, CategoryName;
END;
$$;

---------------------------------------
-- PostgreSQL version of tsp_GetSlotCustomerDiscountCalc
CREATE OR REPLACE FUNCTION tcasino.tsp_GetSlotCustomerDiscountCalc(
    p_CustomerId BIGINT,
    p_MachineLogId BIGINT,
    p_CardNo VARCHAR,
    p_IsAddDiscount BOOLEAN DEFAULT FALSE
)
RETURNS TABLE(
    NetResult NUMERIC(18,2),
    Result NUMERIC(18,2),
    Discount NUMERIC(18,2),
    AvailableDiscount NUMERIC(18,2),
    DiscountPercentage NUMERIC(18,2),
    DiscountPercentageInt INTEGER,
    Result_Status INTEGER,
    ErrorMessage TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_StartDate DATE;
    v_EndDate DATE;
    v_DiscountAmount NUMERIC(18,2);
    v_DiscountCount BIGINT;
    v_NetResult NUMERIC(18,2);
    v_DiscountPercentage NUMERIC(18,2);
    v_SpecialDescription VARCHAR;
    v_SpecialDiscount NUMERIC(18,2);
    v_AvailableDiscount NUMERIC(18,2);
    v_Result INTEGER := 1;
    v_ErrorMessage TEXT;
    v_IsDiscountOK BOOLEAN := FALSE;
    v_DiscountPercentageInt INTEGER;
    v_Description TEXT := '';
    v_AccountId BIGINT;
BEGIN
    -- Get gaming dates
    v_StartDate := tcasino.fn_GetCageGamingDate();
    v_EndDate := v_StartDate;

    -- Get discount amount and count
    SELECT 
        COALESCE(SUM(Amount), 0),
        COALESCE(COUNT(*), 0)
    INTO v_DiscountAmount, v_DiscountCount
    FROM tcasino.T_OperatorTransactions ot
    INNER JOIN tcasino.T_Account ac ON ac.AccountId = ot.AccountId AND ac.CustomerId = p_CustomerId
    WHERE ot.GamingDate BETWEEN v_StartDate AND v_EndDate
    AND ot.OperationType IN (4, 11, 17, 18);

    -- Create temporary table for balance calculation
    DROP TABLE IF EXISTS temp_self_calc_balance;
    
    CREATE TEMP TABLE temp_self_calc_balance (
        NetResult NUMERIC(18,2),
        Result NUMERIC(18,2),
        Discount NUMERIC(18,2)
    );

    -- Insert calculated balance
    INSERT INTO temp_self_calc_balance (NetResult, Result, Discount)
    SELECT 
        ROUND(x.Result + x.Discount, 2) as NetResult,
        x.Result,
        x.Discount
    FROM (
        SELECT 
            ROUND(tcasino.fn_GetCustomerWinLossByCageDates(p_CustomerId, v_StartDate, v_EndDate), 2) as Result,
            tcasino.fn_GetCustomerGetDiscounts(p_CustomerId, v_StartDate, v_EndDate) as Discount
    ) x;

    -- Get net result
    SELECT NetResult INTO v_NetResult FROM temp_self_calc_balance;
    v_NetResult := COALESCE(v_NetResult, 0);

    -- Get discount percentage based on net result
    SELECT DiscountRate INTO v_DiscountPercentage
    FROM tcasino.T_DiscountRates 
    WHERE (MinAmount * -1) >= v_NetResult 
    ORDER BY MinAmount DESC 
    LIMIT 1;
    
    v_DiscountPercentage := COALESCE(v_DiscountPercentage, 0);

    -- Check for special discount
    SELECT Description INTO v_SpecialDescription
    FROM tcasino.T_CustomerNotes c 
    WHERE c.CustomerId = p_CustomerId 
    AND c.NoteType = 1 
    AND c.DeletedDate IS NULL 
    AND Description LIKE '%[%]%' 
    ORDER BY InfoNoteId DESC 
    LIMIT 1;

    -- Extract special discount percentage
    BEGIN
        SELECT REPLACE(value, '%', '') INTO v_SpecialDiscount
        FROM unnest(string_to_array(v_SpecialDescription, ' ')) as value
        WHERE value LIKE '%[%]%'
        LIMIT 1;
        
        v_SpecialDiscount := CAST(v_SpecialDiscount AS NUMERIC(18,2));
    EXCEPTION
        WHEN OTHERS THEN
            v_SpecialDiscount := 0;
    END;

    v_SpecialDiscount := COALESCE(v_SpecialDiscount, 0);
    
    IF v_SpecialDiscount > 0 THEN
        v_DiscountPercentage := v_SpecialDiscount;
    END IF;

    -- Convert percentage to decimal
    v_DiscountPercentage := v_DiscountPercentage / 100;

    -- Calculate available discount
    SELECT 
        CASE 
            WHEN x.NetResult < 0 THEN 
                ROUND(ABS(x.NetResult * v_DiscountPercentage) - v_DiscountAmount, 2)
            ELSE 0 
        END
    INTO v_AvailableDiscount
    FROM temp_self_calc_balance x;

    IF v_AvailableDiscount < 0 THEN
        v_AvailableDiscount := 0;
    END IF;
    
    v_AvailableDiscount := ROUND(v_AvailableDiscount, 2);

    -- Debug output
    RAISE NOTICE 'AvailableDiscount: %', v_AvailableDiscount;

    -- Check if discount should be added
    IF p_IsAddDiscount = TRUE THEN
        v_Result := -1;
        v_ErrorMessage := 'NO DISCOUNT AVAILABLE';
        
        IF v_AvailableDiscount > 0 THEN
            v_IsDiscountOK := TRUE;
            v_Result := 1;
            v_ErrorMessage := 'Good luck! Please re-insert your card.';
        END IF;
    END IF;

    v_DiscountPercentageInt := CAST(v_DiscountPercentage * 100 AS INTEGER);

    -- Return the main result
    RETURN QUERY
    SELECT 
        x.NetResult,
        x.Result,
        x.Discount,
        v_AvailableDiscount as AvailableDiscount,
        v_DiscountPercentage as DiscountPercentage,
        v_DiscountPercentageInt as DiscountPercentageInt,
        v_Result as Result_Status,
        v_ErrorMessage::TEXT as ErrorMessage
    FROM temp_self_calc_balance x;

    -- Add discount transaction if approved
    IF v_IsDiscountOK = TRUE THEN
        BEGIN
            v_Description := 'Result:' || v_NetResult::TEXT || '  %' || v_DiscountPercentageInt::TEXT;
        EXCEPTION
            WHEN OTHERS THEN
                v_Description := '';
        END;

        -- Get account ID
        SELECT AccountId INTO v_AccountId 
        FROM tcasino.T_Account 
        WHERE CustomerId = p_CustomerId;

        -- Call the operator transactions procedure
        PERFORM tcasino.tsp_InsOperatorTransactions(
            p_UserId := 1,
            p_CardNo := p_CardNo,
            p_AccountId := v_AccountId,
            p_Amount := v_AvailableDiscount,
            p_RealAmount := v_AvailableDiscount,
            p_Discount := 0,
            p_OperationType := 4,
            p_Description := v_Description,
            p_CageId := 1,
            p_SourceCurrencyId := 3,
            p_SourceAmount := v_AvailableDiscount,
            p_OperationDeviceInfo := '1.1.1.1'
        );
    END IF;

    -- Clean up
    DROP TABLE IF EXISTS temp_self_calc_balance;

END;
$$;
------------------------------------------
-- PostgreSQL version of tsp_GetProductsAndSubCategoriesSlot
CREATE OR REPLACE FUNCTION tcasino.tsp_GetProductsAndSubCategoriesSlot(
    p_CategoryId BIGINT,
    p_CustomerId BIGINT,
    p_Type BIGINT  -- 1: Product, 2: Category
)
RETURNS TABLE(
    -- Product fields (when Type = 1)
    ProductId BIGINT,
    ProductName VARCHAR,
    CategoryId BIGINT,
    ProductCost NUMERIC(18,2),
    ProductPrice NUMERIC(18,2),
    IsActive BOOLEAN,
    OrderKey INTEGER,
    CreatedDate TIMESTAMP,
    UpdatedDate TIMESTAMP,
    CreatedBy INTEGER,
    UpdatedBy INTEGER,
    ProductDescription TEXT,
    ProductImage VARCHAR,
    FullCategoryName VARCHAR,
    CategoryName VARCHAR,
    
    -- Category fields (when Type = 2)
    ParentCategoryId BIGINT,
    CategoryDescription TEXT,
    CategoryImage VARCHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Return products if Type = 1
    IF p_Type = 1 THEN
        RETURN QUERY
        SELECT 
            p.ProductId,
            p.ProductName,
            p.CategoryId,
            p.ProductCost,
            p.ProductPrice,
            p.IsActive,
            p.OrderKey,
            p.CreatedDate,
            p.UpdatedDate,
            p.CreatedBy,
            p.UpdatedBy,
            p.ProductDescription,
            p.ProductImage,
            pc.FullCategoryName,
            pc.CategoryName,
            NULL::BIGINT as ParentCategoryId,  -- Null for product queries
            NULL::TEXT as CategoryDescription,
            NULL::VARCHAR as CategoryImage
        FROM tcasino.T_Products p
        INNER JOIN tcasino.T_ProductCategories pc ON pc.CategoryId = p.CategoryId
        WHERE p.CategoryId = p_CategoryId AND p.IsActive = TRUE
        ORDER BY p.OrderKey, p.ProductName;
    END IF;
    
    -- Return categories if Type = 2
    IF p_Type = 2 THEN
        RETURN QUERY
        SELECT 
            NULL::BIGINT as ProductId,           -- Null for category queries
            NULL::VARCHAR as ProductName,
            CategoryId,
            NULL::NUMERIC(18,2) as ProductCost,
            NULL::NUMERIC(18,2) as ProductPrice,
            IsActive,
            OrderKey,
            CreatedDate,
            UpdatedDate,
            CreatedBy,
            UpdatedBy,
            NULL::TEXT as ProductDescription,
            NULL::VARCHAR as ProductImage,
            NULL::VARCHAR as FullCategoryName,
            CategoryName,
            ParentCategoryId,
            CategoryDescription,
            CategoryImage
        FROM tcasino.T_ProductCategories
        WHERE ParentCategoryId = p_CategoryId AND IsActive = TRUE
        ORDER BY OrderKey, CategoryName;
    END IF;
END;
$$;