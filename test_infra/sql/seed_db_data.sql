--
-- PostgreSQL database dump
--

-- Dumped from database version 14.2 (Debian 14.2-1.pgdg110+1)
-- Dumped by pg_dump version 14.2 (Debian 14.2-1.pgdg110+1)

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
-- Data for Name: datasets; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.datasets (id, title, description, deposition_date, release_date, last_modified_date, related_database_entries, related_database_links, dataset_publications, dataset_citations, sample_type, organism_name, organism_taxid, tissue_name, tissue_id, cell_name, cell_type_id, cell_strain_name, cell_strain_id, sample_preparation, grid_preparation, other_setup, s3_prefix, https_prefix, key_photo_url, key_photo_thumbnail_url, cell_component_name, cell_component_id, deposition_id) FROM stdin;
10000	S. pombe cells with defocus	Defocus cryo-electron tomography of S. pombe cryo-FIB lamellae with comprehensive annotations of structures and macromolecules	2023-04-01	2023-06-01	2023-06-01	EMPIAR-10988, EMD-14412, EMD-14413, EMD-14415, EMD-14417, EMD-14418, EMD-14419, EMD-14420	\N	doi:10.1101/2022.04.12.488077, doi:10.1038/s41592-022-01746-2	\N	organism	Schizosaccharomyces pombe	4896	\N	\N	\N	\N	Schizosaccharomyces pombe 972h-	NCBITaxon:284812	buffer_ph: 7.0, vitrification_cryogen_name: ETHANE, instance_type: subtomogram_averaging_preparation	model: Quantifoil R2/1, material: COPPER, mesh: 200, support_film_film_type_id: 1, support_film_film_material: CARBON, support_film_film_topology: HOLEY, support_film_instance_type: support_film, pretreatment_type_: GLOW DISCHARGE	\N	s3://cryoet-data-portal-staging/10000/	https://files.cryoetdataportal.cziscience.com/10000/	https://files.cryoetdataportal.cziscience.com/10000/Images/snapshot.gif	https://files.cryoetdataportal.cziscience.com/10000/Images/thumbnail.gif	\N	\N	10000
\.


--
-- Data for Name: runs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.runs (id, dataset_id, name, s3_prefix, https_prefix) FROM stdin;
5	10000	TS_026	s3://cryoet-data-portal-staging/10000/TS_026/	https://files.cryoetdataportal.cziscience.com/10000/TS_026/
\.


--
-- Data for Name: tomogram_voxel_spacings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tomogram_voxel_spacings (id, run_id, voxel_spacing, s3_prefix, https_prefix) FROM stdin;
4	5	13.48	s3://cryoet-data-portal-staging/10000/TS_026/Tomograms/VoxelSpacing13.480/	https://files.cryoetdataportal.cziscience.com/10000/TS_026/Tomograms/VoxelSpacing13.480/
\.


--
-- Data for Name: annotations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.annotations (id, s3_metadata_path, https_metadata_path, deposition_date, release_date, last_modified_date, annotation_publication, annotation_method, ground_truth_status, object_name, object_id, object_description, object_state, object_count, confidence_precision, confidence_recall, ground_truth_used, tomogram_voxel_spacing_id, annotation_software, is_curator_recommended, method_type, deposition_id) FROM stdin;
2	s3://cryoet-data-portal-staging/10000/TS_026/Tomograms/VoxelSpacing13.480/Annotations/100-fatty_acid_synthase_complex-1.0.json	https://files.cryoetdataportal.cziscience.com/10000/TS_026/Tomograms/VoxelSpacing13.480/Annotations/100-fatty_acid_synthase_complex-1.0.json	2023-04-01	2023-06-01	2023-06-01	EMPIAR-10988, EMD-14412, EMD-14413, EMD-14415, EMD-14417, EMD-14418, EMD-14419, EMD-14420, 10.1101/2022.04.12.488077	Cumulative template-matching trained 2D CNN predictions + visual filtering + distance constraints + manual addition	t	fatty acid synthase complex	GO:0005835	\N	\N	16	\N	\N	\N	4	pyTOM + Keras	t	hybrid	10000
3	s3://cryoet-data-portal-staging/10000/TS_026/Tomograms/VoxelSpacing13.480/Annotations/101-cytosolic_ribosome-1.0.json	https://files.cryoetdataportal.cziscience.com/10000/TS_026/Tomograms/VoxelSpacing13.480/Annotations/101-cytosolic_ribosome-1.0.json	2023-04-01	2023-06-01	2023-06-01	EMPIAR-10988, EMD-14412, EMD-14413, EMD-14415, EMD-14417, EMD-14418, EMD-14419, EMD-14420, 10.1101/2022.04.12.488077	Cumulative template-matching trained 2D CNN predictions + visual filtering + distance constraints + manual addition	t	cytosolic ribosome	GO:0022626	\N	\N	838	\N	\N	\N	4	pyTOM + Keras	t	hybrid	10000
4	s3://cryoet-data-portal-staging/10000/TS_026/Tomograms/VoxelSpacing13.480/Annotations/102-cytoplasm-1.0.json	https://files.cryoetdataportal.cziscience.com/10000/TS_026/Tomograms/VoxelSpacing13.480/Annotations/102-cytoplasm-1.0.json	2023-04-01	2023-06-01	2023-06-01	EMPIAR-10988, EMD-14412, EMD-14413, EMD-14415, EMD-14417, EMD-14418, EMD-14419, EMD-14420, 10.1101/2022.04.12.488077	spectrum equalization filter + 2D CNN prediction + manual correction	t	cytoplasm	GO:0005737	\N	\N	0	\N	\N	\N	4	Keras + AMIRA	t	hybrid	10000
5	s3://cryoet-data-portal-staging/10000/TS_026/Tomograms/VoxelSpacing13.480/Annotations/104-vesicle-1.0.json	https://files.cryoetdataportal.cziscience.com/10000/TS_026/Tomograms/VoxelSpacing13.480/Annotations/104-vesicle-1.0.json	2023-04-01	2023-06-01	2023-06-01	EMPIAR-10988, EMD-14412, EMD-14413, EMD-14415, EMD-14417, EMD-14418, EMD-14419, EMD-14420, 10.1101/2022.04.12.488077	spectrum equalization filter + 2D CNN prediction + manual correction	t	vesicle	GO:0031982	\N	\N	0	\N	\N	\N	4	Keras + AMIRA	t	hybrid	10000
6	s3://cryoet-data-portal-staging/10000/TS_026/Tomograms/VoxelSpacing13.480/Annotations/106-endoplasmic_reticulum-1.0.json	https://files.cryoetdataportal.cziscience.com/10000/TS_026/Tomograms/VoxelSpacing13.480/Annotations/106-endoplasmic_reticulum-1.0.json	2023-04-01	2023-06-01	2023-06-01	EMPIAR-10988, EMD-14412, EMD-14413, EMD-14415, EMD-14417, EMD-14418, EMD-14419, EMD-14420, 10.1101/2022.04.12.488077	spectrum equalization filter + 2D CNN prediction + manual correction	t	endoplasmic reticulum	GO:0005783	\N	\N	0	\N	\N	\N	4	Keras + AMIRA	t	hybrid	10000
7	s3://cryoet-data-portal-staging/10000/TS_026/Tomograms/VoxelSpacing13.480/Annotations/109-vacuole-1.0.json	https://files.cryoetdataportal.cziscience.com/10000/TS_026/Tomograms/VoxelSpacing13.480/Annotations/109-vacuole-1.0.json	2023-04-01	2023-06-01	2023-06-01	EMPIAR-10988, EMD-14412, EMD-14413, EMD-14415, EMD-14417, EMD-14418, EMD-14419, EMD-14420, 10.1101/2022.04.12.488077	spectrum equalization filter + 2D CNN prediction + manual correction	t	vacuole	GO:0005773	\N	\N	0	\N	\N	\N	4	Keras + AMIRA	t	hybrid	10000
8	s3://cryoet-data-portal-staging/10000/TS_026/Tomograms/VoxelSpacing13.480/Annotations/112-multivesicular_body-1.0.json	https://files.cryoetdataportal.cziscience.com/10000/TS_026/Tomograms/VoxelSpacing13.480/Annotations/112-multivesicular_body-1.0.json	2023-04-01	2023-06-01	2023-06-01	EMPIAR-10988, EMD-14412, EMD-14413, EMD-14415, EMD-14417, EMD-14418, EMD-14419, EMD-14420, 10.1101/2022.04.12.488077	spectrum equalization filter + 2D CNN prediction + manual correction	t	multivesicular body	GO:0005771	\N	\N	0	\N	\N	\N	4	Keras + AMIRA	t	hybrid	10000
9	s3://cryoet-data-portal-staging/10000/TS_026/Tomograms/VoxelSpacing13.480/Annotations/114-membrane-1.0.json	https://files.cryoetdataportal.cziscience.com/10000/TS_026/Tomograms/VoxelSpacing13.480/Annotations/114-membrane-1.0.json	2023-04-01	2023-06-01	2023-06-01	EMPIAR-10988, EMD-14412, EMD-14413, EMD-14415, EMD-14417, EMD-14418, EMD-14419, EMD-14420, 10.1101/2022.04.12.488077	3D CNN prediction + manual correction	t	membrane	GO:0016020	\N	\N	0	\N	\N	\N	4	Keras + AMIRA	t	hybrid	10000
\.


--
-- Data for Name: annotation_authors; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.annotation_authors (id, annotation_id, name, orcid, corresponding_author_status, primary_annotator_status, email, affiliation_name, affiliation_address, affiliation_identifier, author_list_order, primary_author_status) FROM stdin;
4	2	Sara Goetz	0000-0002-9903-3667	\N	t	\N	\N	\N	\N	1	t
5	2	Irene de Teresa Trueba	0000-0002-4691-9501	\N	\N	\N	\N	\N	\N	2	\N
6	2	Alexander Mattausch	0000-0003-0901-8701	\N	\N	\N	\N	\N	\N	3	\N
7	2	Frosina Stojanovska	0000-0002-4327-1068	\N	\N	\N	\N	\N	\N	4	\N
8	2	Christian Eugen Zimmerli	0000-0003-4388-1349	\N	\N	\N	\N	\N	\N	5	\N
9	2	Mauricio Toro-Nahuelpan	0000-0001-5333-3640	\N	\N	\N	\N	\N	\N	6	\N
10	2	Dorothy W. C. Cheng	\N	\N	\N	\N	\N	\N	\N	7	\N
11	2	Fergus Tollervey	\N	\N	\N	\N	\N	\N	\N	8	\N
12	2	Constantin Pape	0000-0001-6562-7187	\N	\N	\N	\N	\N	\N	9	\N
13	2	Martin Beck	0000-0002-7397-1321	\N	\N	\N	\N	\N	\N	10	\N
14	2	Alba Diz-Munoz	0000-0001-6864-8901	\N	\N	\N	\N	\N	\N	11	\N
15	2	Anna Kreshuk	0000-0003-1334-6388	\N	\N	\N	\N	\N	\N	12	\N
16	2	Julia Mahamid	0000-0001-6968-041X	t	\N	\N	\N	\N	\N	13	\N
17	2	Judith B. Zaugg	0000-0001-8324-4040	t	\N	\N	\N	\N	\N	14	\N
18	3	Sara Goetz	0000-0002-9903-3667	\N	t	\N	\N	\N	\N	1	t
19	3	Irene de Teresa Trueba	0000-0002-4691-9501	\N	\N	\N	\N	\N	\N	2	\N
20	3	Alexander Mattausch	0000-0003-0901-8701	\N	\N	\N	\N	\N	\N	3	\N
21	3	Frosina Stojanovska	0000-0002-4327-1068	\N	\N	\N	\N	\N	\N	4	\N
22	3	Christian Eugen Zimmerli	0000-0003-4388-1349	\N	\N	\N	\N	\N	\N	5	\N
23	3	Mauricio Toro-Nahuelpan	0000-0001-5333-3640	\N	\N	\N	\N	\N	\N	6	\N
24	3	Dorothy W. C. Cheng	\N	\N	\N	\N	\N	\N	\N	7	\N
25	3	Fergus Tollervey	\N	\N	\N	\N	\N	\N	\N	8	\N
26	3	Constantin Pape	0000-0001-6562-7187	\N	\N	\N	\N	\N	\N	9	\N
27	3	Martin Beck	0000-0002-7397-1321	\N	\N	\N	\N	\N	\N	10	\N
28	3	Alba Diz-Munoz	0000-0001-6864-8901	\N	\N	\N	\N	\N	\N	11	\N
29	3	Anna Kreshuk	0000-0003-1334-6388	\N	\N	\N	\N	\N	\N	12	\N
30	3	Julia Mahamid	0000-0001-6968-041X	t	\N	\N	\N	\N	\N	13	\N
31	3	Judith B. Zaugg	0000-0001-8324-4040	t	\N	\N	\N	\N	\N	14	\N
32	4	Sara Goetz	0000-0002-9903-3667	\N	t	\N	\N	\N	\N	1	t
33	4	Irene de Teresa Trueba	0000-0002-4691-9501	\N	\N	\N	\N	\N	\N	2	\N
34	4	Alexander Mattausch	0000-0003-0901-8701	\N	\N	\N	\N	\N	\N	3	\N
35	4	Frosina Stojanovska	0000-0002-4327-1068	\N	\N	\N	\N	\N	\N	4	\N
36	4	Christian Eugen Zimmerli	0000-0003-4388-1349	\N	\N	\N	\N	\N	\N	5	\N
37	4	Mauricio Toro-Nahuelpan	0000-0001-5333-3640	\N	\N	\N	\N	\N	\N	6	\N
38	4	Dorothy W. C. Cheng	\N	\N	\N	\N	\N	\N	\N	7	\N
39	4	Fergus Tollervey	\N	\N	\N	\N	\N	\N	\N	8	\N
40	4	Constantin Pape	0000-0001-6562-7187	\N	\N	\N	\N	\N	\N	9	\N
41	4	Martin Beck	0000-0002-7397-1321	\N	\N	\N	\N	\N	\N	10	\N
42	4	Alba Diz-Munoz	0000-0001-6864-8901	\N	\N	\N	\N	\N	\N	11	\N
43	4	Anna Kreshuk	0000-0003-1334-6388	\N	\N	\N	\N	\N	\N	12	\N
44	4	Julia Mahamid	0000-0001-6968-041X	t	\N	\N	\N	\N	\N	13	\N
45	4	Judith B. Zaugg	0000-0001-8324-4040	t	\N	\N	\N	\N	\N	14	\N
46	5	Sara Goetz	0000-0002-9903-3667	\N	t	\N	\N	\N	\N	1	t
47	5	Irene de Teresa Trueba	0000-0002-4691-9501	\N	\N	\N	\N	\N	\N	2	\N
48	5	Alexander Mattausch	0000-0003-0901-8701	\N	\N	\N	\N	\N	\N	3	\N
49	5	Frosina Stojanovska	0000-0002-4327-1068	\N	\N	\N	\N	\N	\N	4	\N
50	5	Christian Eugen Zimmerli	0000-0003-4388-1349	\N	\N	\N	\N	\N	\N	5	\N
51	5	Mauricio Toro-Nahuelpan	0000-0001-5333-3640	\N	\N	\N	\N	\N	\N	6	\N
52	5	Dorothy W. C. Cheng	\N	\N	\N	\N	\N	\N	\N	7	\N
53	5	Fergus Tollervey	\N	\N	\N	\N	\N	\N	\N	8	\N
54	5	Constantin Pape	0000-0001-6562-7187	\N	\N	\N	\N	\N	\N	9	\N
55	5	Martin Beck	0000-0002-7397-1321	\N	\N	\N	\N	\N	\N	10	\N
56	5	Alba Diz-Munoz	0000-0001-6864-8901	\N	\N	\N	\N	\N	\N	11	\N
57	5	Anna Kreshuk	0000-0003-1334-6388	\N	\N	\N	\N	\N	\N	12	\N
58	5	Julia Mahamid	0000-0001-6968-041X	t	\N	\N	\N	\N	\N	13	\N
59	5	Judith B. Zaugg	0000-0001-8324-4040	t	\N	\N	\N	\N	\N	14	\N
60	6	Sara Goetz	0000-0002-9903-3667	\N	t	\N	\N	\N	\N	1	t
61	6	Irene de Teresa Trueba	0000-0002-4691-9501	\N	\N	\N	\N	\N	\N	2	\N
62	6	Alexander Mattausch	0000-0003-0901-8701	\N	\N	\N	\N	\N	\N	3	\N
63	6	Frosina Stojanovska	0000-0002-4327-1068	\N	\N	\N	\N	\N	\N	4	\N
64	6	Christian Eugen Zimmerli	0000-0003-4388-1349	\N	\N	\N	\N	\N	\N	5	\N
65	6	Mauricio Toro-Nahuelpan	0000-0001-5333-3640	\N	\N	\N	\N	\N	\N	6	\N
66	6	Dorothy W. C. Cheng	\N	\N	\N	\N	\N	\N	\N	7	\N
67	6	Fergus Tollervey	\N	\N	\N	\N	\N	\N	\N	8	\N
68	6	Constantin Pape	0000-0001-6562-7187	\N	\N	\N	\N	\N	\N	9	\N
69	6	Martin Beck	0000-0002-7397-1321	\N	\N	\N	\N	\N	\N	10	\N
70	6	Alba Diz-Munoz	0000-0001-6864-8901	\N	\N	\N	\N	\N	\N	11	\N
71	6	Anna Kreshuk	0000-0003-1334-6388	\N	\N	\N	\N	\N	\N	12	\N
72	6	Julia Mahamid	0000-0001-6968-041X	t	\N	\N	\N	\N	\N	13	\N
73	6	Judith B. Zaugg	0000-0001-8324-4040	t	\N	\N	\N	\N	\N	14	\N
74	7	Sara Goetz	0000-0002-9903-3667	\N	t	\N	\N	\N	\N	1	t
75	7	Irene de Teresa Trueba	0000-0002-4691-9501	\N	\N	\N	\N	\N	\N	2	\N
76	7	Alexander Mattausch	0000-0003-0901-8701	\N	\N	\N	\N	\N	\N	3	\N
77	7	Frosina Stojanovska	0000-0002-4327-1068	\N	\N	\N	\N	\N	\N	4	\N
78	7	Christian Eugen Zimmerli	0000-0003-4388-1349	\N	\N	\N	\N	\N	\N	5	\N
79	7	Mauricio Toro-Nahuelpan	0000-0001-5333-3640	\N	\N	\N	\N	\N	\N	6	\N
80	7	Dorothy W. C. Cheng	\N	\N	\N	\N	\N	\N	\N	7	\N
81	7	Fergus Tollervey	\N	\N	\N	\N	\N	\N	\N	8	\N
82	7	Constantin Pape	0000-0001-6562-7187	\N	\N	\N	\N	\N	\N	9	\N
83	7	Martin Beck	0000-0002-7397-1321	\N	\N	\N	\N	\N	\N	10	\N
84	7	Alba Diz-Munoz	0000-0001-6864-8901	\N	\N	\N	\N	\N	\N	11	\N
85	7	Anna Kreshuk	0000-0003-1334-6388	\N	\N	\N	\N	\N	\N	12	\N
86	7	Julia Mahamid	0000-0001-6968-041X	t	\N	\N	\N	\N	\N	13	\N
87	7	Judith B. Zaugg	0000-0001-8324-4040	t	\N	\N	\N	\N	\N	14	\N
88	8	Sara Goetz	0000-0002-9903-3667	\N	t	\N	\N	\N	\N	1	t
89	8	Irene de Teresa Trueba	0000-0002-4691-9501	\N	\N	\N	\N	\N	\N	2	\N
90	8	Alexander Mattausch	0000-0003-0901-8701	\N	\N	\N	\N	\N	\N	3	\N
91	8	Frosina Stojanovska	0000-0002-4327-1068	\N	\N	\N	\N	\N	\N	4	\N
92	8	Christian Eugen Zimmerli	0000-0003-4388-1349	\N	\N	\N	\N	\N	\N	5	\N
93	8	Mauricio Toro-Nahuelpan	0000-0001-5333-3640	\N	\N	\N	\N	\N	\N	6	\N
94	8	Dorothy W. C. Cheng	\N	\N	\N	\N	\N	\N	\N	7	\N
95	8	Fergus Tollervey	\N	\N	\N	\N	\N	\N	\N	8	\N
96	8	Constantin Pape	0000-0001-6562-7187	\N	\N	\N	\N	\N	\N	9	\N
97	8	Martin Beck	0000-0002-7397-1321	\N	\N	\N	\N	\N	\N	10	\N
98	8	Alba Diz-Munoz	0000-0001-6864-8901	\N	\N	\N	\N	\N	\N	11	\N
99	8	Anna Kreshuk	0000-0003-1334-6388	\N	\N	\N	\N	\N	\N	12	\N
100	8	Julia Mahamid	0000-0001-6968-041X	t	\N	\N	\N	\N	\N	13	\N
101	8	Judith B. Zaugg	0000-0001-8324-4040	t	\N	\N	\N	\N	\N	14	\N
102	9	Sara Goetz	0000-0002-9903-3667	\N	t	\N	\N	\N	\N	1	t
103	9	Irene de Teresa Trueba	0000-0002-4691-9501	\N	\N	\N	\N	\N	\N	2	\N
104	9	Alexander Mattausch	0000-0003-0901-8701	\N	\N	\N	\N	\N	\N	3	\N
105	9	Frosina Stojanovska	0000-0002-4327-1068	\N	\N	\N	\N	\N	\N	4	\N
106	9	Christian Eugen Zimmerli	0000-0003-4388-1349	\N	\N	\N	\N	\N	\N	5	\N
107	9	Mauricio Toro-Nahuelpan	0000-0001-5333-3640	\N	\N	\N	\N	\N	\N	6	\N
108	9	Dorothy W. C. Cheng	\N	\N	\N	\N	\N	\N	\N	7	\N
109	9	Fergus Tollervey	\N	\N	\N	\N	\N	\N	\N	8	\N
110	9	Constantin Pape	0000-0001-6562-7187	\N	\N	\N	\N	\N	\N	9	\N
111	9	Martin Beck	0000-0002-7397-1321	\N	\N	\N	\N	\N	\N	10	\N
112	9	Alba Diz-Munoz	0000-0001-6864-8901	\N	\N	\N	\N	\N	\N	11	\N
113	9	Anna Kreshuk	0000-0003-1334-6388	\N	\N	\N	\N	\N	\N	12	\N
114	9	Julia Mahamid	0000-0001-6968-041X	t	\N	\N	\N	\N	\N	13	\N
115	9	Judith B. Zaugg	0000-0001-8324-4040	t	\N	\N	\N	\N	\N	14	\N
\.


--
-- Data for Name: annotation_files; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.annotation_files (id, annotation_id, shape_type, format, https_path, s3_path, is_visualization_default) FROM stdin;
4	2	Point	ndjson	https://files.cryoetdataportal.cziscience.com/10000/TS_026/Tomograms/VoxelSpacing13.480/Annotations/100-fatty_acid_synthase_complex-1.0_point.ndjson	s3://cryoet-data-portal-staging/10000/TS_026/Tomograms/VoxelSpacing13.480/Annotations/100-fatty_acid_synthase_complex-1.0_point.ndjson	f
5	3	Point	ndjson	https://files.cryoetdataportal.cziscience.com/10000/TS_026/Tomograms/VoxelSpacing13.480/Annotations/101-cytosolic_ribosome-1.0_point.ndjson	s3://cryoet-data-portal-staging/10000/TS_026/Tomograms/VoxelSpacing13.480/Annotations/101-cytosolic_ribosome-1.0_point.ndjson	t
6	4	SegmentationMask	zarr	https://files.cryoetdataportal.cziscience.com/10000/TS_026/Tomograms/VoxelSpacing13.480/Annotations/102-cytoplasm-1.0_segmentationmask.zarr	s3://cryoet-data-portal-staging/10000/TS_026/Tomograms/VoxelSpacing13.480/Annotations/102-cytoplasm-1.0_segmentationmask.zarr	f
7	4	SegmentationMask	mrc	https://files.cryoetdataportal.cziscience.com/10000/TS_026/Tomograms/VoxelSpacing13.480/Annotations/102-cytoplasm-1.0_segmentationmask.mrc	s3://cryoet-data-portal-staging/10000/TS_026/Tomograms/VoxelSpacing13.480/Annotations/102-cytoplasm-1.0_segmentationmask.mrc	f
8	5	SegmentationMask	zarr	https://files.cryoetdataportal.cziscience.com/10000/TS_026/Tomograms/VoxelSpacing13.480/Annotations/104-vesicle-1.0_segmentationmask.zarr	s3://cryoet-data-portal-staging/10000/TS_026/Tomograms/VoxelSpacing13.480/Annotations/104-vesicle-1.0_segmentationmask.zarr	f
9	5	SegmentationMask	mrc	https://files.cryoetdataportal.cziscience.com/10000/TS_026/Tomograms/VoxelSpacing13.480/Annotations/104-vesicle-1.0_segmentationmask.mrc	s3://cryoet-data-portal-staging/10000/TS_026/Tomograms/VoxelSpacing13.480/Annotations/104-vesicle-1.0_segmentationmask.mrc	f
10	6	SegmentationMask	zarr	https://files.cryoetdataportal.cziscience.com/10000/TS_026/Tomograms/VoxelSpacing13.480/Annotations/106-endoplasmic_reticulum-1.0_segmentationmask.zarr	s3://cryoet-data-portal-staging/10000/TS_026/Tomograms/VoxelSpacing13.480/Annotations/106-endoplasmic_reticulum-1.0_segmentationmask.zarr	t
11	6	SegmentationMask	mrc	https://files.cryoetdataportal.cziscience.com/10000/TS_026/Tomograms/VoxelSpacing13.480/Annotations/106-endoplasmic_reticulum-1.0_segmentationmask.mrc	s3://cryoet-data-portal-staging/10000/TS_026/Tomograms/VoxelSpacing13.480/Annotations/106-endoplasmic_reticulum-1.0_segmentationmask.mrc	t
12	7	SegmentationMask	zarr	https://files.cryoetdataportal.cziscience.com/10000/TS_026/Tomograms/VoxelSpacing13.480/Annotations/109-vacuole-1.0_segmentationmask.zarr	s3://cryoet-data-portal-staging/10000/TS_026/Tomograms/VoxelSpacing13.480/Annotations/109-vacuole-1.0_segmentationmask.zarr	f
13	7	SegmentationMask	mrc	https://files.cryoetdataportal.cziscience.com/10000/TS_026/Tomograms/VoxelSpacing13.480/Annotations/109-vacuole-1.0_segmentationmask.mrc	s3://cryoet-data-portal-staging/10000/TS_026/Tomograms/VoxelSpacing13.480/Annotations/109-vacuole-1.0_segmentationmask.mrc	f
14	8	SegmentationMask	zarr	https://files.cryoetdataportal.cziscience.com/10000/TS_026/Tomograms/VoxelSpacing13.480/Annotations/112-multivesicular_body-1.0_segmentationmask.zarr	s3://cryoet-data-portal-staging/10000/TS_026/Tomograms/VoxelSpacing13.480/Annotations/112-multivesicular_body-1.0_segmentationmask.zarr	f
15	8	SegmentationMask	mrc	https://files.cryoetdataportal.cziscience.com/10000/TS_026/Tomograms/VoxelSpacing13.480/Annotations/112-multivesicular_body-1.0_segmentationmask.mrc	s3://cryoet-data-portal-staging/10000/TS_026/Tomograms/VoxelSpacing13.480/Annotations/112-multivesicular_body-1.0_segmentationmask.mrc	f
16	9	SegmentationMask	zarr	https://files.cryoetdataportal.cziscience.com/10000/TS_026/Tomograms/VoxelSpacing13.480/Annotations/114-membrane-1.0_segmentationmask.zarr	s3://cryoet-data-portal-staging/10000/TS_026/Tomograms/VoxelSpacing13.480/Annotations/114-membrane-1.0_segmentationmask.zarr	f
17	9	SegmentationMask	mrc	https://files.cryoetdataportal.cziscience.com/10000/TS_026/Tomograms/VoxelSpacing13.480/Annotations/114-membrane-1.0_segmentationmask.mrc	s3://cryoet-data-portal-staging/10000/TS_026/Tomograms/VoxelSpacing13.480/Annotations/114-membrane-1.0_segmentationmask.mrc	f
\.


--
-- Data for Name: dataset_authors; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dataset_authors (id, name, orcid, corresponding_author_status, email, affiliation_name, affiliation_address, affiliation_identifier, dataset_id, primary_author_status, author_list_order) FROM stdin;
4	Irene de Teresa Trueba	0000-0002-4691-9501	\N	\N	\N	\N	\N	10000	t	1
5	Sara Goetz	0000-0002-9903-3667	\N	\N	\N	\N	\N	10000	\N	2
6	Alexander Mattausch	0000-0003-0901-8701	\N	\N	\N	\N	\N	10000	\N	3
7	Frosina Stojanovska	0000-0002-4327-1068	\N	\N	\N	\N	\N	10000	\N	4
8	Christian Eugen Zimmerli	0000-0003-4388-1349	\N	\N	\N	\N	\N	10000	\N	5
9	Mauricio Toro-Nahuelpan	0000-0001-5333-3640	\N	\N	\N	\N	\N	10000	\N	6
10	Dorothy W. C. Cheng	\N	\N	\N	\N	\N	\N	10000	\N	7
11	Fergus Tollervey	\N	\N	\N	\N	\N	\N	10000	\N	8
12	Constantin Pape	0000-0001-6562-7187	\N	\N	\N	\N	\N	10000	\N	9
13	Martin Beck	0000-0002-7397-1321	\N	\N	\N	\N	\N	10000	\N	10
14	Alba Diz-Munoz	0000-0001-6864-8901	\N	\N	\N	\N	\N	10000	\N	11
15	Anna Kreshuk	0000-0003-1334-6388	\N	\N	\N	\N	\N	10000	\N	12
16	Julia Mahamid	0000-0001-6968-041X	t	\N	\N	\N	\N	10000	\N	13
17	Judith B. Zaugg	0000-0001-8324-4040	t	\N	\N	\N	\N	10000	\N	14
\.


--
-- Data for Name: dataset_funding; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dataset_funding (id, dataset_id, funding_agency_name, grant_id) FROM stdin;
4	10000	European Research Council (ERC)	760067
\.


--
-- Data for Name: depositions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.depositions (id, title, description, deposition_date, release_date, last_modified_date, related_database_entries, deposition_publications, deposition_types, s3_prefix, https_prefix) FROM stdin;
10000	TBA	TBA	2023-04-01	2023-06-01	2023-06-01	\N	\N	dataset	s3://cryoetportal-output-test/depositions_metadata/10000/	https://files.cryoetdataportal.cziscience.com/depositions_metadata/10000/
\.


--
-- Data for Name: deposition_authors; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.deposition_authors (id, name, orcid, corresponding_author_status, email, affiliation_name, affiliation_address, affiliation_identifier, deposition_id, primary_author_status, author_list_order) FROM stdin;
57	Irene de Teresa Trueba	0000-0002-4691-9501	\N	\N	\N	\N	\N	10000	t	1
58	Sara Goetz	0000-0002-9903-3667	\N	\N	\N	\N	\N	10000	\N	2
59	Alexander Mattausch	0000-0003-0901-8701	\N	\N	\N	\N	\N	10000	\N	3
60	Frosina Stojanovska	0000-0002-4327-1068	\N	\N	\N	\N	\N	10000	\N	4
61	Christian Eugen Zimmerli	0000-0003-4388-1349	\N	\N	\N	\N	\N	10000	\N	5
62	Mauricio Toro-Nahuelpan	0000-0001-5333-3640	\N	\N	\N	\N	\N	10000	\N	6
63	Dorothy W. C. Cheng	\N	\N	\N	\N	\N	\N	10000	\N	7
64	Fergus Tollervey	\N	\N	\N	\N	\N	\N	10000	\N	8
65	Constantin Pape	0000-0001-6562-7187	\N	\N	\N	\N	\N	10000	\N	9
66	Martin Beck	0000-0002-7397-1321	\N	\N	\N	\N	\N	10000	\N	10
67	Alba Diz-Munoz	0000-0001-6864-8901	\N	\N	\N	\N	\N	10000	\N	11
68	Anna Kreshuk	0000-0003-1334-6388	\N	\N	\N	\N	\N	10000	\N	12
69	Julia Mahamid	0000-0001-6968-041X	t	\N	\N	\N	\N	10000	\N	13
70	Judith B. Zaugg	0000-0001-8324-4040	t	\N	\N	\N	\N	10000	\N	14
\.


--
-- Data for Name: tiltseries; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tiltseries (id, run_id, s3_mrc_bin1, s3_omezarr_dir, https_mrc_bin1, https_omezarr_dir, s3_collection_metadata, https_collection_metadata, s3_angle_list, https_angle_list, s3_alignment_file, https_alignment_file, acceleration_voltage, spherical_aberration_constant, microscope_manufacturer, microscope_model, microscope_energy_filter, microscope_phase_plate, microscope_image_corrector, microscope_additional_info, camera_manufacturer, camera_model, tilt_min, tilt_max, tilt_range, tilt_step, tilting_scheme, tilt_axis, total_flux, data_acquisition_software, related_empiar_entry, binning_from_frames, tilt_series_quality, is_aligned, pixel_spacing, aligned_tiltseries_binning, frames_count, deposition_id) FROM stdin;
3	5	s3://cryoet-data-portal-staging/10000/TS_026/TiltSeries/TS_026.mrc	s3://cryoet-data-portal-staging/10000/TS_026/TiltSeries/TS_026.zarr	https://files.cryoetdataportal.cziscience.com/10000/TS_026/TiltSeries/TS_026.mrc	https://files.cryoetdataportal.cziscience.com/10000/TS_026/TiltSeries/TS_026.zarr	s3://cryoet-data-portal-staging/10000/TS_026/TiltSeries/TS_026.mdoc	https://files.cryoetdataportal.cziscience.com/10000/TS_026/TiltSeries/TS_026.mdoc	s3://cryoet-data-portal-staging/10000/TS_026/TiltSeries/TS_026.rawtlt	https://files.cryoetdataportal.cziscience.com/10000/TS_026/TiltSeries/TS_026.rawtlt	s3://cryoet-data-portal-staging/10000/TS_026/TiltSeries/TS_026.xf	https://files.cryoetdataportal.cziscience.com/10000/TS_026/TiltSeries/TS_026.xf	300000	2.7	TFS	Krios	GIF Quantum LS	\N	\N	\N	Gatan	K2 SUMMIT	-40.0	58.0	98.0	2.0	Dose symmetric from 0.0 degrees	84.7	122.0	SerialEM	EMPIAR-10988	1.0	5	f	3.3702	\N	51	10000
\.


--
-- Data for Name: tomogram_type; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tomogram_type (value, description) FROM stdin;
CANONICAL
UNKOWN
\.


--
-- Data for Name: tomograms; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tomograms (id, name, size_x, size_y, size_z, voxel_spacing, fiducial_alignment_status, reconstruction_method, reconstruction_software, processing, processing_software, tomogram_version, is_canonical, s3_omezarr_dir, https_omezarr_dir, s3_mrc_scale0, https_mrc_scale0, scale0_dimensions, scale1_dimensions, scale2_dimensions, ctf_corrected, tomogram_voxel_spacing_id, offset_x, offset_y, offset_z, affine_transformation_matrix, key_photo_url, key_photo_thumbnail_url, neuroglancer_config, type, deposition_id) FROM stdin;
3	TS_026	960	928	1000	13.48	NON_FIDUCIAL	WBP	IMOD	raw	\N	1	t	s3://cryoet-data-portal-staging/10000/TS_026/Tomograms/VoxelSpacing13.480/CanonicalTomogram/TS_026.zarr	https://files.cryoetdataportal.cziscience.com/10000/TS_026/Tomograms/VoxelSpacing13.480/CanonicalTomogram/TS_026.zarr	s3://cryoet-data-portal-staging/10000/TS_026/Tomograms/VoxelSpacing13.480/CanonicalTomogram/TS_026.mrc	https://files.cryoetdataportal.cziscience.com/10000/TS_026/Tomograms/VoxelSpacing13.480/CanonicalTomogram/TS_026.mrc	960,928,1000	480,464,500	240,232,250	f	4	0	0	0	{{1,0,0,0},{0,1,0,0},{0,0,1,0},{0,0,0,1}}	https://files.cryoetdataportal.cziscience.com/10000/TS_026/Tomograms/VoxelSpacing13.480/KeyPhotos/key-photo-snapshot.png	https://files.cryoetdataportal.cziscience.com/10000/TS_026/Tomograms/VoxelSpacing13.480/KeyPhotos/key-photo-thumbnail.png	{"dimensions":{"x":[1.3481000000000001e-09,"m"],"y":[1.3481000000000001e-09,"m"],"z":[1.3481000000000001e-09,"m"]},"crossSectionScale":2.5,"projectionOrientation":[0.3826834323650898,0.0,0.0,0.9238795325112867],"layers":[{"type":"image","name":"TS_026","source":{"url":"zarr://https://files.cryoetdataportal.cziscience.com/10000/TS_026/Tomograms/VoxelSpacing13.480/CanonicalTomogram/TS_026.zarr","transform":{"outputDimensions":{"x":[1.3481000000000001e-09,"m"],"y":[1.3481000000000001e-09,"m"],"z":[1.3481000000000001e-09,"m"]},"inputDimensions":{"x":[1.3481000000000001e-09,"m"],"y":[1.3481000000000001e-09,"m"],"z":[1.3481000000000001e-09,"m"]}}},"opacity":0.51,"tab":"rendering","visible":true,"shader":"#uicontrol invlerp normalized\\n\\nvoid main() {\\n  emitGrayscale(normalized());\\n}\\n","shaderControls":{"normalized":{"range":[-25.87576985359192,30.21921420097351],"window":[-28.68051905632019,33.023963403701785]}},"_position":[480.0,464.0,500.0],"_crossSectionScale":2.5,"_projectionScale":1100.0},{"type":"annotation","name":"100 fatty acid synthase complex point","source":{"url":"precomputed://https://files.cryoetdataportal.cziscience.com/10000/TS_026/Tomograms/VoxelSpacing13.480/NeuroglancerPrecompute/100-fatty_acid_synthase_complex-1.0_point","transform":{"outputDimensions":{"x":[1.3481000000000001e-09,"m"],"y":[1.3481000000000001e-09,"m"],"z":[1.3481000000000001e-09,"m"]},"inputDimensions":{"x":[1.3481000000000001e-09,"m"],"y":[1.3481000000000001e-09,"m"],"z":[1.3481000000000001e-09,"m"]}}},"tab":"rendering","shader":"#uicontrol float pointScale slider(min=0.01, max=2.0, default=1.0, step=0.01)\\n#uicontrol float opacity slider(min=0, max=1, default=1)\\n#uicontrol vec3 color color(default=\\"#80ff00\\")\\n\\nvoid main() {\\n  setColor(vec4(color, opacity));\\n  setPointMarkerSize(pointScale * prop_diameter());\\n  setPointMarkerBorderWidth(0.1);\\n}","visible":false},{"type":"annotation","name":"101 cytosolic ribosome point","source":{"url":"precomputed://https://files.cryoetdataportal.cziscience.com/10000/TS_026/Tomograms/VoxelSpacing13.480/NeuroglancerPrecompute/101-cytosolic_ribosome-1.0_point","transform":{"outputDimensions":{"x":[1.3481000000000001e-09,"m"],"y":[1.3481000000000001e-09,"m"],"z":[1.3481000000000001e-09,"m"]},"inputDimensions":{"x":[1.3481000000000001e-09,"m"],"y":[1.3481000000000001e-09,"m"],"z":[1.3481000000000001e-09,"m"]}}},"tab":"rendering","shader":"#uicontrol float pointScale slider(min=0.01, max=2.0, default=1.0, step=0.01)\\n#uicontrol float opacity slider(min=0, max=1, default=1)\\n#uicontrol vec3 color color(default=\\"#80ffff\\")\\n\\nvoid main() {\\n  setColor(vec4(color, opacity));\\n  setPointMarkerSize(pointScale * prop_diameter());\\n  setPointMarkerBorderWidth(0.1);\\n}","visible":true},{"type":"segmentation","name":"102 cytoplasm segmentation","source":{"url":"precomputed://https://files.cryoetdataportal.cziscience.com/10000/TS_026/Tomograms/VoxelSpacing13.480/NeuroglancerPrecompute/102-cytoplasm-1.0_segmentationmask","transform":{"outputDimensions":{"x":[1.3481000000000001e-09,"m"],"y":[1.3481000000000001e-09,"m"],"z":[1.3481000000000001e-09,"m"]},"inputDimensions":{"x":[1.3481000000000001e-09,"m"],"y":[1.3481000000000001e-09,"m"],"z":[1.3481000000000001e-09,"m"]}}},"tab":"rendering","selectedAlpha":1,"hoverHighlight":false,"segments":[1],"segmentDefaultColor":"#9150af","visible":false},{"type":"segmentation","name":"104 vesicle segmentation","source":{"url":"precomputed://https://files.cryoetdataportal.cziscience.com/10000/TS_026/Tomograms/VoxelSpacing13.480/NeuroglancerPrecompute/104-vesicle-1.0_segmentationmask","transform":{"outputDimensions":{"x":[1.3481000000000001e-09,"m"],"y":[1.3481000000000001e-09,"m"],"z":[1.3481000000000001e-09,"m"]},"inputDimensions":{"x":[1.3481000000000001e-09,"m"],"y":[1.3481000000000001e-09,"m"],"z":[1.3481000000000001e-09,"m"]}}},"tab":"rendering","selectedAlpha":1,"hoverHighlight":false,"segments":[1],"segmentDefaultColor":"#00ff80","visible":false},{"type":"segmentation","name":"106 endoplasmic reticulum segmentation","source":{"url":"precomputed://https://files.cryoetdataportal.cziscience.com/10000/TS_026/Tomograms/VoxelSpacing13.480/NeuroglancerPrecompute/106-endoplasmic_reticulum-1.0_segmentationmask","transform":{"outputDimensions":{"x":[1.3481000000000001e-09,"m"],"y":[1.3481000000000001e-09,"m"],"z":[1.3481000000000001e-09,"m"]},"inputDimensions":{"x":[1.3481000000000001e-09,"m"],"y":[1.3481000000000001e-09,"m"],"z":[1.3481000000000001e-09,"m"]}}},"tab":"rendering","selectedAlpha":1,"hoverHighlight":false,"segments":[1],"segmentDefaultColor":"#ff0080","visible":true},{"type":"segmentation","name":"109 vacuole segmentation","source":{"url":"precomputed://https://files.cryoetdataportal.cziscience.com/10000/TS_026/Tomograms/VoxelSpacing13.480/NeuroglancerPrecompute/109-vacuole-1.0_segmentationmask","transform":{"outputDimensions":{"x":[1.3481000000000001e-09,"m"],"y":[1.3481000000000001e-09,"m"],"z":[1.3481000000000001e-09,"m"]},"inputDimensions":{"x":[1.3481000000000001e-09,"m"],"y":[1.3481000000000001e-09,"m"],"z":[1.3481000000000001e-09,"m"]}}},"tab":"rendering","selectedAlpha":1,"hoverHighlight":false,"segments":[1],"segmentDefaultColor":"#000080","visible":false},{"type":"segmentation","name":"112 multivesicular body segmentation","source":{"url":"precomputed://https://files.cryoetdataportal.cziscience.com/10000/TS_026/Tomograms/VoxelSpacing13.480/NeuroglancerPrecompute/112-multivesicular_body-1.0_segmentationmask","transform":{"outputDimensions":{"x":[1.3481000000000001e-09,"m"],"y":[1.3481000000000001e-09,"m"],"z":[1.3481000000000001e-09,"m"]},"inputDimensions":{"x":[1.3481000000000001e-09,"m"],"y":[1.3481000000000001e-09,"m"],"z":[1.3481000000000001e-09,"m"]}}},"tab":"rendering","selectedAlpha":1,"hoverHighlight":false,"segments":[1],"segmentDefaultColor":"#03a3c3","visible":false},{"type":"segmentation","name":"114 membrane segmentation","source":{"url":"precomputed://https://files.cryoetdataportal.cziscience.com/10000/TS_026/Tomograms/VoxelSpacing13.480/NeuroglancerPrecompute/114-membrane-1.0_segmentationmask","transform":{"outputDimensions":{"x":[1.3481000000000001e-09,"m"],"y":[1.3481000000000001e-09,"m"],"z":[1.3481000000000001e-09,"m"]},"inputDimensions":{"x":[1.3481000000000001e-09,"m"],"y":[1.3481000000000001e-09,"m"],"z":[1.3481000000000001e-09,"m"]}}},"tab":"rendering","selectedAlpha":1,"hoverHighlight":false,"segments":[1],"segmentDefaultColor":"#9f9d81","visible":false},{"type":"annotation","name":"115 membrane point","source":{"url":"precomputed://https://files.cryoetdataportal.cziscience.com/10000/TS_026/Tomograms/VoxelSpacing13.480/NeuroglancerPrecompute/115-membrane-1.0_instancesegmentation","transform":{"outputDimensions":{"x":[1.3481000000000001e-09,"m"],"y":[1.3481000000000001e-09,"m"],"z":[1.3481000000000001e-09,"m"]},"inputDimensions":{"x":[1.3481000000000001e-09,"m"],"y":[1.3481000000000001e-09,"m"],"z":[1.3481000000000001e-09,"m"]}}},"tab":"rendering","shader":"#uicontrol float pointScale slider(min=0.01, max=2.0, default=1.0, step=0.01)\\n#uicontrol float opacity slider(min=0, max=1, default=1)\\n\\nvoid main() {\\n  setColor(vec4(prop_color(), opacity));\\n  setPointMarkerSize(pointScale * prop_diameter());\\n  setPointMarkerBorderWidth(0.1);\\n}","visible":false},{"type":"segmentation","name":"115 membrane segmentation","source":{"url":"precomputed://https://files.cryoetdataportal.cziscience.com/10000/TS_026/Tomograms/VoxelSpacing13.480/NeuroglancerPrecompute/115-membrane-1.0_segmentationmask","transform":{"outputDimensions":{"x":[1.3481000000000001e-09,"m"],"y":[1.3481000000000001e-09,"m"],"z":[1.3481000000000001e-09,"m"]},"inputDimensions":{"x":[1.3481000000000001e-09,"m"],"y":[1.3481000000000001e-09,"m"],"z":[1.3481000000000001e-09,"m"]}}},"tab":"rendering","selectedAlpha":1,"hoverHighlight":false,"segments":[1],"segmentDefaultColor":"#2d4ffe","visible":false},{"type":"segmentation","name":"116 membrane segmentation","source":{"url":"precomputed://https://files.cryoetdataportal.cziscience.com/10000/TS_026/Tomograms/VoxelSpacing13.480/NeuroglancerPrecompute/116-membrain_seg_prediction-1.0_segmentationmask","transform":{"outputDimensions":{"x":[1.3481000000000001e-09,"m"],"y":[1.3481000000000001e-09,"m"],"z":[1.3481000000000001e-09,"m"]},"inputDimensions":{"x":[1.3481000000000001e-09,"m"],"y":[1.3481000000000001e-09,"m"],"z":[1.3481000000000001e-09,"m"]}}},"tab":"rendering","selectedAlpha":1,"hoverHighlight":false,"segments":[1],"segmentDefaultColor":"#ae370c","visible":true}],"selectedLayer":{"visible":true,"layer":"TS_026"},"crossSectionBackgroundColor":"#000000","layout":"4panel","position":[480.0,464.0,500.0],"projectionScale":1100.0,"deposition_id":10000}	CANONICAL	10000
\.


--
-- Data for Name: tomogram_authors; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tomogram_authors (id, tomogram_id, author_list_order, name, orcid, corresponding_author_status, primary_author_status, email, affiliation_name, affiliation_address, affiliation_identifier) FROM stdin;
3	3	1	Irene de Teresa Trueba	0000-0002-4691-9501	\N	t	\N	\N	\N	\N
4	3	2	Sara Goetz	0000-0002-9903-3667	\N	\N	\N	\N	\N	\N
5	3	3	Alexander Mattausch	0000-0003-0901-8701	\N	\N	\N	\N	\N	\N
6	3	4	Frosina Stojanovska	0000-0002-4327-1068	\N	\N	\N	\N	\N	\N
7	3	5	Christian Eugen Zimmerli	0000-0003-4388-1349	\N	\N	\N	\N	\N	\N
8	3	6	Mauricio Toro-Nahuelpan	0000-0001-5333-3640	\N	\N	\N	\N	\N	\N
9	3	7	Dorothy W. C. Cheng	\N	\N	\N	\N	\N	\N	\N
10	3	8	Fergus Tollervey	\N	\N	\N	\N	\N	\N	\N
11	3	9	Constantin Pape	0000-0001-6562-7187	\N	\N	\N	\N	\N	\N
12	3	10	Martin Beck	0000-0002-7397-1321	\N	\N	\N	\N	\N	\N
13	3	11	Alba Diz-Munoz	0000-0001-6864-8901	\N	\N	\N	\N	\N	\N
14	3	12	Anna Kreshuk	0000-0003-1334-6388	\N	\N	\N	\N	\N	\N
15	3	13	Julia Mahamid	0000-0001-6968-041X	t	\N	\N	\N	\N	\N
16	3	14	Judith B. Zaugg	0000-0001-8324-4040	t	\N	\N	\N	\N	\N
\.


--
-- Name: annotation_authors_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.annotation_authors_id_seq', 115, true);


--
-- Name: annotation_files_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.annotation_files_id_seq', 17, true);


--
-- Name: annotations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.annotations_id_seq', 9, true);


--
-- Name: dataset_authors_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dataset_authors_id_seq', 17, true);


--
-- Name: dataset_funding_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dataset_funding_id_seq', 4, true);


--
-- Name: deposition_authors_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.deposition_authors_id_seq', 70, true);


--
-- Name: depositions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.depositions_id_seq', 1, false);


--
-- Name: runs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.runs_id_seq', 5, true);


--
-- Name: tiltseries_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tiltseries_id_seq', 3, true);


--
-- Name: tomogram_authors_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tomogram_authors_id_seq', 16, true);


--
-- Name: tomogram_voxel_spacing_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tomogram_voxel_spacing_id_seq', 4, true);


--
-- Name: tomograms_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tomograms_id_seq', 3, true);


--
-- PostgreSQL database dump complete
--
