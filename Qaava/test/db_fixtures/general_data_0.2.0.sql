--
-- PostgreSQL database dump
--

-- Dumped from database version 12.2
-- Dumped by pg_dump version 12.4 (Ubuntu 12.4-0ubuntu0.20.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: dokumentti; Type: TABLE DATA; Schema: kaavan_lisatiedot; Owner: -
--

INSERT INTO kaavan_lisatiedot.dokumentti (gid, otsikko, uri, gid_kieli, gid_dokumenttityyppi)
VALUES (1, 'Listätietoa lähteestä B', NULL, 2, 2);
INSERT INTO kaavan_lisatiedot.dokumentti (gid, otsikko, uri, gid_kieli, gid_dokumenttityyppi)
VALUES (3, 'Kukkakauppias', NULL, 2, 2);


--
-- Data for Name: taustakartta; Type: TABLE DATA; Schema: kaavan_lisatiedot; Owner: -
--


--
-- Data for Name: kuvaustyyli; Type: TABLE DATA; Schema: koodistot; Owner: -
--


--
-- Data for Name: yleiskaava; Type: TABLE DATA; Schema: yleiskaava; Owner: -
--

INSERT INTO yleiskaava.yleiskaava (gid, uuid, geom, nimi, kaavatunnus, laatija, viimeisin_muokkaaja, vahvistaja,
                                   luomispvm, poistamispvm, voimaantulopvm, kumoamispvm, gid_taustakartta, gid_kieli,
                                   gid_kuvaustyyli, gid_vaihetieto, gid_kaavatyyppi, gid_dokumentti)
VALUES (1, 'f6b0549e-d265-40d2-b4ee-30d63eed3e0e',
        '01060000A0250F00000100000001030000800100000007000000AED3C01B365E7641574F77E3948959410000000000000000C9CA2614625E764167498A39268A594100000000000000001AABAB61845E76411A50024C0E8A5941000000000000000023D31676A65E76417BD7B388A989594100000000000000009FDA5164865E7641A9FC49341C8959410000000000000000924777BB4F5E764155C96C72008959410000000000000000AED3C01B365E7641574F77E3948959410000000000000000',
        'Testing', NULL, NULL, NULL, NULL, '2020-09-04 14:12:53.127', NULL, NULL, NULL, NULL, 1, NULL, 1, 8, NULL);
INSERT INTO yleiskaava.yleiskaava (gid, uuid, geom, nimi, kaavatunnus, laatija, viimeisin_muokkaaja, vahvistaja,
                                   luomispvm, poistamispvm, voimaantulopvm, kumoamispvm, gid_taustakartta, gid_kieli,
                                   gid_kuvaustyyli, gid_vaihetieto, gid_kaavatyyppi, gid_dokumentti)
VALUES (3, '6a82d752-6374-4c13-a98b-dac52a5b71f5',
        '01060000A0250F00000100000001030000800100000007000000505D5AD0FA5D7641D52FEBA5CE8C5941000000000000000056FF62C14E5E76414CEF79234E8D594100000000000000005DE6C5EA765E76413398E373DF8C59410000000000000000E064AF7A6D5E764107D2F5EE498C594100000000000000007E4AE39C365E76419F7DC60DEA8B59410000000000000000B6C05A790E5E7641FE1E9B36E98B59410000000000000000505D5AD0FA5D7641D52FEBA5CE8C59410000000000000000',
        'Viimeinen testi', '123', NULL, NULL, NULL, '2020-09-04 15:29:31.797', NULL, NULL, NULL, NULL, 1, NULL, 1, 8,
        NULL);
INSERT INTO yleiskaava.yleiskaava (gid, uuid, geom, nimi, kaavatunnus, laatija, viimeisin_muokkaaja, vahvistaja,
                                   luomispvm, poistamispvm, voimaantulopvm, kumoamispvm, gid_taustakartta, gid_kieli,
                                   gid_kuvaustyyli, gid_vaihetieto, gid_kaavatyyppi, gid_dokumentti)
VALUES (2, '7e88fcd5-9541-459c-be25-8e1d0d2f44b2',
        '01060000A0250F000001000000010300008001000000060000003FF2001C825E76417D4C46EF918A59410000000000000000AB8B38B4A05E7641B18B6C68178B59410000000000000000705C8BD6CD5E764124C290CFE28A594100000000000000002929E2FCD15E764140AE8EDD3F8A594100000000000000002557DBD8BE5E76414B991854028A594100000000000000003FF2001C825E76417D4C46EF918A59410000000000000000',
        'Sannala', NULL, NULL, 'sanna_gispo', NULL, '2020-09-04 15:10:04.3', NULL, NULL, NULL, NULL, 1, NULL, 1, 1,
        NULL);
INSERT INTO yleiskaava.yleiskaava (gid, uuid, geom, nimi, kaavatunnus, laatija, viimeisin_muokkaaja, vahvistaja,
                                   luomispvm, poistamispvm, voimaantulopvm, kumoamispvm, gid_taustakartta, gid_kieli,
                                   gid_kuvaustyyli, gid_vaihetieto, gid_kaavatyyppi, gid_dokumentti)
VALUES (5, 'f52815a4-239f-4b1e-96d2-4ca9f3f5535a',
        '01060000A0250F000001000000010300008001000000060000001A3B2CAD105F76410CF036D5FA8B59410000000000000000AB484357285F7641A015B91C828C594100000000000000001E0EED0D935F7641676A5941A58C59410000000000000000F98406E5975F764173D5A411858B594100000000000000006994F5A3285F7641E67DE45E4F8B594100000000000000001A3B2CAD105F76410CF036D5FA8B59410000000000000000',
        'Testikaava', NULL, NULL, 'sanna_gispo', NULL, '2020-09-08 13:33:55.955', NULL, NULL, NULL, NULL, 1, NULL, 1, 1,
        NULL);


--
-- Data for Name: many_dokumentti_has_many_yleiskaava; Type: TABLE DATA; Schema: kaavan_lisatiedot; Owner: -
--

INSERT INTO kaavan_lisatiedot.many_dokumentti_has_many_yleiskaava (gid_dokumentti, uuid_yleiskaava)
VALUES (1, '6a82d752-6374-4c13-a98b-dac52a5b71f5');
INSERT INTO kaavan_lisatiedot.many_dokumentti_has_many_yleiskaava (gid_dokumentti, uuid_yleiskaava)
VALUES (1, '7e88fcd5-9541-459c-be25-8e1d0d2f44b2');


--
-- Data for Name: numeerinen_lisatieto; Type: TABLE DATA; Schema: kaavan_lisatiedot; Owner: -
--


--
-- Data for Name: hilucs; Type: TABLE DATA; Schema: koodistot; Owner: -
--


--
-- Data for Name: hsrcl; Type: TABLE DATA; Schema: koodistot; Owner: -
--


--
-- Data for Name: kaavamaarays; Type: TABLE DATA; Schema: koodistot; Owner: -
--

INSERT INTO koodistot.kaavamaarays (uuid, luontipvm, otsikko, maaraysteksti)
VALUES ('b509f712-4e59-4262-9ed1-741df377729a', '2020-09-04 14:26:02.537', 'Testausmääräys', NULL);
INSERT INTO koodistot.kaavamaarays (uuid, luontipvm, otsikko, maaraysteksti)
VALUES ('d6ee9c90-ebef-4f60-8ac2-b8fbc069e7aa', '2020-09-04 15:10:20.143', 'Toimiihan tämä', NULL);
INSERT INTO koodistot.kaavamaarays (uuid, luontipvm, otsikko, maaraysteksti)
VALUES ('db99a8d6-02c2-42af-ac17-e3fde5084ccd', '2020-09-08 13:34:54.347', 'yleismääräys1', 'plaaplapla');


--
-- Data for Name: teema; Type: TABLE DATA; Schema: koodistot; Owner: -
--

INSERT INTO koodistot.teema (gid, nimi)
VALUES (0, 'Viherkaava');


--
-- Data for Name: kaavaelementti; Type: TABLE DATA; Schema: yleiskaava; Owner: -
--

INSERT INTO yleiskaava.kaavaelementti (gid, uuid, geom_polygon, geom_line, geom_point, pinta_ala, pituus,
                                       viimeisin_muokkaaja, luontipvm, periytynytkohde, uuid_yleiskaava,
                                       gid_kaavaelementti_tyyppi, gid_dokumentti)
VALUES (2, '16c2263f-3ff2-4ce2-8e2b-64ecbc97d130', NULL, NULL,
        '01040000A0250F0000010000000101000080919D6770865E76416E1D77A8108B59410000000000000000', NULL, NULL, NULL,
        '2020-09-04 13:42:17.495', false, NULL, 73, NULL);
INSERT INTO yleiskaava.kaavaelementti (gid, uuid, geom_polygon, geom_line, geom_point, pinta_ala, pituus,
                                       viimeisin_muokkaaja, luontipvm, periytynytkohde, uuid_yleiskaava,
                                       gid_kaavaelementti_tyyppi, gid_dokumentti)
VALUES (3, '4a38d59f-43e7-49da-9ce6-1d840e013314', NULL, NULL,
        '01040000A0250F0000010000000101000080A820BF9E895E76417E45D8682E8A59410000000000000000', NULL, NULL, NULL,
        '2020-09-04 13:42:37.29', false, 'f6b0549e-d265-40d2-b4ee-30d63eed3e0e', 71, NULL);
INSERT INTO yleiskaava.kaavaelementti (gid, uuid, geom_polygon, geom_line, geom_point, pinta_ala, pituus,
                                       viimeisin_muokkaaja, luontipvm, periytynytkohde, uuid_yleiskaava,
                                       gid_kaavaelementti_tyyppi, gid_dokumentti)
VALUES (4, '8f07a49c-e72b-4ae6-b609-5ff9febe7d12', NULL,
        '01050000A0250F0000010000000102000080040000001D6A37A15C5E764177AE6110578A5941000000000000000046D311DA6A5E7641DE27F298FE8A59410000000000000000AE62BCB67C5E76412CAD5F5B718B5941000000000000000058A9105E995E7641FBC3C41F928B59410000000000000000',
        NULL, NULL, NULL, NULL, '2020-09-04 10:47:49.072', false, 'f6b0549e-d265-40d2-b4ee-30d63eed3e0e', 45, NULL);
INSERT INTO yleiskaava.kaavaelementti (gid, uuid, geom_polygon, geom_line, geom_point, pinta_ala, pituus,
                                       viimeisin_muokkaaja, luontipvm, periytynytkohde, uuid_yleiskaava,
                                       gid_kaavaelementti_tyyppi, gid_dokumentti)
VALUES (6, '36567a11-a01c-4872-80b7-be96a9c22065', NULL, NULL, NULL, NULL, NULL, 'sanna_gispo',
        '2020-09-04 15:04:44.653', true, NULL, NULL, 1);


--
-- Data for Name: maankayttoalue; Type: TABLE DATA; Schema: yleiskaava; Owner: -
--

INSERT INTO yleiskaava.maankayttoalue (gid, uuid, geom, nimi, pinta_ala, viimeisin_muokkaaja, luontipvm,
                                       periytynytkohde, gid_maankayttoluokka, uuid_yleiskaava, gid_dokumentti)
VALUES (3, '403c4108-f9fe-49df-94dd-d14930468bf2',
        '01060000A0250F00000100000001030000800100000006000000B0DE9F6E185E7641B58DB5E97C8A594100000000000000005280A8452F5E7641589840D7E88A5941000000000000000059C41805425E764138922B5BCF8A59410000000000000000C6BACC20425E76418BFF8BD2358A5941000000000000000048B84177215E7641FC16A6BC188A59410000000000000000B0DE9F6E185E7641B58DB5E97C8A59410000000000000000',
        'Kukkakauppa', 401075.4, 'sanna_gispo', '2020-09-04 14:30:54.81', true, 14,
        'f6b0549e-d265-40d2-b4ee-30d63eed3e0e', 3);
INSERT INTO yleiskaava.maankayttoalue (gid, uuid, geom, nimi, pinta_ala, viimeisin_muokkaaja, luontipvm,
                                       periytynytkohde, gid_maankayttoluokka, uuid_yleiskaava, gid_dokumentti)
VALUES (4, 'a7b9731b-061a-401c-b147-bff9dba4070b',
        '01060000A0250F000001000000010300008001000000070000000EF3FE92315E7641DDC51ED4038B5941000000000000000089D2304E445E764176BDEB23908B5941000000000000000096479EA7605E76417E7958F25A8B59410000000000000000B3B8F65F4E5E7641D0B85624FA8A5941000000000000000059C41805425E764138922B5BCF8A594100000000000000005280A8452F5E7641589840D7E88A594100000000000000000EF3FE92315E7641DDC51ED4038B59410000000000000000',
        NULL, 315365.72, 'sanna_gispo', '2020-09-04 14:34:45.711', true, 14, 'f6b0549e-d265-40d2-b4ee-30d63eed3e0e', 3);
INSERT INTO yleiskaava.maankayttoalue (gid, uuid, geom, nimi, pinta_ala, viimeisin_muokkaaja, luontipvm,
                                       periytynytkohde, gid_maankayttoluokka, uuid_yleiskaava, gid_dokumentti)
VALUES (5, 'c76f5716-48be-4bc8-8ff1-44342f15a4c7',
        '01060000A0250F0000010000000103000080010000000600000098218711215F7641F28D7C04E68B594100000000000000001A54AF773A5F76412E74C9D5558C5941000000000000000018E89E24475F7641183F4DCA438C594100000000000000000E91F36A525F76417CCBA349AB8B59410000000000000000535F7788315F7641E40AABFF8F8B5941000000000000000098218711215F7641F28D7C04E68B59410000000000000000',
        'testimaankäyttö', 384537.75, 'sanna_gispo', '2020-09-08 13:36:01.177', true, 14,
        'f52815a4-239f-4b1e-96d2-4ca9f3f5535a', 1);
INSERT INTO yleiskaava.maankayttoalue (gid, uuid, geom, nimi, pinta_ala, viimeisin_muokkaaja, luontipvm,
                                       periytynytkohde, gid_maankayttoluokka, uuid_yleiskaava, gid_dokumentti)
VALUES (6, '59ebc284-fb29-492f-a1e9-9f062afc76be',
        '01060000A0250F000001000000010300008001000000060000009EBA59D2A95E7641517BBA1F3C8B594100000000000000003177137CAD5E76412218CC50468B5941000000000000000013E977D7AF5E764100D963AB3C8B59410000000000000000D90855B8AE5E76418450FCB22D8B594100000000000000000FAE7BA4A95E7641547935C9338B594100000000000000009EBA59D2A95E7641517BBA1F3C8B59410000000000000000',
        NULL, 6153.0566, 'sanna_gispo', '2020-09-08 13:46:43.774', false, 1, '7e88fcd5-9541-459c-be25-8e1d0d2f44b2',
        NULL);


--
-- Data for Name: many_kaavaelementti_has_many_kaavamaarays; Type: TABLE DATA; Schema: yleiskaava; Owner: -
--


--
-- Data for Name: many_kaavaelementti_has_many_numeerinen_lisatieto; Type: TABLE DATA; Schema: yleiskaava; Owner: -
--


--
-- Data for Name: many_kaavaelementti_has_many_teema; Type: TABLE DATA; Schema: yleiskaava; Owner: -
--


--
-- Data for Name: many_maankayttoalue_has_many_kaavamaarays; Type: TABLE DATA; Schema: yleiskaava; Owner: -
--

INSERT INTO yleiskaava.many_maankayttoalue_has_many_kaavamaarays (uuid_maankayttoalue, uuid_kaavamaarays)
VALUES ('403c4108-f9fe-49df-94dd-d14930468bf2', 'b509f712-4e59-4262-9ed1-741df377729a');
INSERT INTO yleiskaava.many_maankayttoalue_has_many_kaavamaarays (uuid_maankayttoalue, uuid_kaavamaarays)
VALUES ('a7b9731b-061a-401c-b147-bff9dba4070b', 'b509f712-4e59-4262-9ed1-741df377729a');


--
-- Data for Name: many_maankayttoalue_has_many_numeerinen_lisatieto; Type: TABLE DATA; Schema: yleiskaava; Owner: -
--


--
-- Data for Name: many_maankayttoalue_has_many_teema; Type: TABLE DATA; Schema: yleiskaava; Owner: -
--


--
-- Data for Name: many_yleiskaava_has_many_kaavamaarays; Type: TABLE DATA; Schema: yleiskaava; Owner: -
--

INSERT INTO yleiskaava.many_yleiskaava_has_many_kaavamaarays (uuid_yleiskaava, uuid_kaavamaarays)
VALUES ('f6b0549e-d265-40d2-b4ee-30d63eed3e0e', 'b509f712-4e59-4262-9ed1-741df377729a');
INSERT INTO yleiskaava.many_yleiskaava_has_many_kaavamaarays (uuid_yleiskaava, uuid_kaavamaarays)
VALUES ('6a82d752-6374-4c13-a98b-dac52a5b71f5', 'b509f712-4e59-4262-9ed1-741df377729a');
INSERT INTO yleiskaava.many_yleiskaava_has_many_kaavamaarays (uuid_yleiskaava, uuid_kaavamaarays)
VALUES ('7e88fcd5-9541-459c-be25-8e1d0d2f44b2', 'd6ee9c90-ebef-4f60-8ac2-b8fbc069e7aa');
INSERT INTO yleiskaava.many_yleiskaava_has_many_kaavamaarays (uuid_yleiskaava, uuid_kaavamaarays)
VALUES ('f52815a4-239f-4b1e-96d2-4ca9f3f5535a', 'b509f712-4e59-4262-9ed1-741df377729a');
INSERT INTO yleiskaava.many_yleiskaava_has_many_kaavamaarays (uuid_yleiskaava, uuid_kaavamaarays)
VALUES ('f52815a4-239f-4b1e-96d2-4ca9f3f5535a', 'db99a8d6-02c2-42af-ac17-e3fde5084ccd');


--
-- Data for Name: many_yleiskaava_has_many_teema; Type: TABLE DATA; Schema: yleiskaava; Owner: -
--

INSERT INTO yleiskaava.many_yleiskaava_has_many_teema (uuid_yleiskaava, gid_teema)
VALUES ('f6b0549e-d265-40d2-b4ee-30d63eed3e0e', 0);
INSERT INTO yleiskaava.many_yleiskaava_has_many_teema (uuid_yleiskaava, gid_teema)
VALUES ('6a82d752-6374-4c13-a98b-dac52a5b71f5', 0);
INSERT INTO yleiskaava.many_yleiskaava_has_many_teema (uuid_yleiskaava, gid_teema)
VALUES ('7e88fcd5-9541-459c-be25-8e1d0d2f44b2', 0);


--
-- Name: dokumentti_gid_seq; Type: SEQUENCE SET; Schema: kaavan_lisatiedot; Owner: -
--

SELECT pg_catalog.setval('kaavan_lisatiedot.dokumentti_gid_seq', 3, true);


--
-- Name: numeerinen_lisatieto_gid_seq; Type: SEQUENCE SET; Schema: kaavan_lisatiedot; Owner: -
--

SELECT pg_catalog.setval('kaavan_lisatiedot.numeerinen_lisatieto_gid_seq', 1, true);


--
-- Name: taustakartta_gid_seq; Type: SEQUENCE SET; Schema: kaavan_lisatiedot; Owner: -
--

SELECT pg_catalog.setval('kaavan_lisatiedot.taustakartta_gid_seq', 1, false);


--
-- Name: dokumenttityyppi_gid_seq; Type: SEQUENCE SET; Schema: koodistot; Owner: -
--

SELECT pg_catalog.setval('koodistot.dokumenttityyppi_gid_seq', 1, false);


--
-- Name: geometria_tyyppi_gid_seq; Type: SEQUENCE SET; Schema: koodistot; Owner: -
--

SELECT pg_catalog.setval('koodistot.geometria_tyyppi_gid_seq', 1, false);


--
-- Name: hilucs_gid_seq; Type: SEQUENCE SET; Schema: koodistot; Owner: -
--

SELECT pg_catalog.setval('koodistot.hilucs_gid_seq', 1, false);


--
-- Name: hsrcl_gid_seq; Type: SEQUENCE SET; Schema: koodistot; Owner: -
--

SELECT pg_catalog.setval('koodistot.hsrcl_gid_seq', 1, false);


--
-- Name: kaavaelementti_tyyppi_gid_seq; Type: SEQUENCE SET; Schema: koodistot; Owner: -
--

SELECT pg_catalog.setval('koodistot.kaavaelementti_tyyppi_gid_seq', 1, false);


--
-- Name: kaavatyyppi_gid_seq; Type: SEQUENCE SET; Schema: koodistot; Owner: -
--

SELECT pg_catalog.setval('koodistot.kaavatyyppi_gid_seq', 1, false);


--
-- Name: kieli_gid_seq; Type: SEQUENCE SET; Schema: koodistot; Owner: -
--

SELECT pg_catalog.setval('koodistot.kieli_gid_seq', 1, false);


--
-- Name: kuvaustyyli_gid_seq; Type: SEQUENCE SET; Schema: koodistot; Owner: -
--

SELECT pg_catalog.setval('koodistot.kuvaustyyli_gid_seq', 1, false);


--
-- Name: maankayttoluokka_gid_seq; Type: SEQUENCE SET; Schema: koodistot; Owner: -
--

SELECT pg_catalog.setval('koodistot.maankayttoluokka_gid_seq', 1, false);


--
-- Name: numeerinen_merkintatyyppi_gid_seq; Type: SEQUENCE SET; Schema: koodistot; Owner: -
--

SELECT pg_catalog.setval('koodistot.numeerinen_merkintatyyppi_gid_seq', 1, false);


--
-- Name: teema_gid_seq; Type: SEQUENCE SET; Schema: koodistot; Owner: -
--

SELECT pg_catalog.setval('koodistot.teema_gid_seq', 1, false);


--
-- Name: tietomalli_metatiedot_gid_seq; Type: SEQUENCE SET; Schema: koodistot; Owner: -
--

SELECT pg_catalog.setval('koodistot.tietomalli_metatiedot_gid_seq', 1, false);


--
-- Name: vaihetieto_gid_seq; Type: SEQUENCE SET; Schema: koodistot; Owner: -
--

SELECT pg_catalog.setval('koodistot.vaihetieto_gid_seq', 1, false);


--
-- Name: kaavaelementti_gid_seq; Type: SEQUENCE SET; Schema: yleiskaava; Owner: -
--

SELECT pg_catalog.setval('yleiskaava.kaavaelementti_gid_seq', 6, true);


--
-- Name: maankayttoalue_gid_seq; Type: SEQUENCE SET; Schema: yleiskaava; Owner: -
--

SELECT pg_catalog.setval('yleiskaava.maankayttoalue_gid_seq', 6, true);


--
-- Name: yleiskaava_gid_seq; Type: SEQUENCE SET; Schema: yleiskaava; Owner: -
--

SELECT pg_catalog.setval('yleiskaava.yleiskaava_gid_seq', 5, true);


--
-- PostgreSQL database dump complete
--

