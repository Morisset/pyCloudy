import pyCloudy as pc


OVN_dic_old = {'host' : 'localhost',
       'user_name' : 'OVN_user',
       'user_passwd' : 'getenv',
       'base_name' : 'OVN',
       'tmp_name' : 'OVN_tmp',
       'pending_table' : '`pending`',
       'master_table' : '`tab`',
       'teion_table' : '`teion`',
       'abion_table' : '`abion`',
       'temis_table' : '`temis`',
       'lines_table' : '`lines`',
       'procIDs_table' : '`procIDs`',
       'seds_table': '`seds`' 
       }

OVN_dic = {'host' : 'localhost',
       'user_name' : 'OVN_admin',
       'user_passwd' : 'getenv',
       'base_name' : '3MdB_17',
       'tmp_name' : 'OVN_tmp',
       'pending_table' : '`pending_17`',
       'master_table' : '`tab_17`',
       'teion_table' : '`teion_17`',
       'abion_table' : '`abion_17`',
       'temis_table' : '`temis_17`',
       'lines_table' : '`lines_17`',
       'procIDs_table' : '`procIDs`',
       'seds_table': '`seds_17`' 
       }

lines_list_old = [('BAC___3646A', 'Bac ', 3646.0, 'BalmHead'), 
              ('COUT__3646A', 'cout', 3646.0, 'OutwardBalmPeak'), 
              ('CREF__3646A', 'cref', 3646.0, 'ReflectedBalmPeak'),
              ('H__1__4861A', 'H  1', 4861.0, 'H I 4861'),
              ('TOTL__4861A', 'TOTL', 4861.0, 'H I 4861'),
            ('H__1__6563A', 'H  1', 6563.0, 'H I 6563'),
            ('H__1__4340A', 'H  1', 4340.0, 'H I 4340'),
            ('H__1__4102A', 'H  1', 4102.0, 'H I 4102'),
            ('H__1__3970A', 'H  1', 3970.0, 'H I 3970'),
            ('H__1__3835A', 'H  1', 3835.0, 'H I 3835'),
            ('H__1__1216A', 'H  1', 1216.0, 'H I 1216'), 
            ('H__1_4051M', 'H  1', 4.051, 'H I 4.051m'),
            ('H__1_2625M', 'H  1', 2.625, 'H I 2.625m'),
            ('H__1_7458M', 'H  1', 7.458, 'H I 7.458m'),
            ('HE_1__5876A', 'He 1', 5876.0, 'He I 5876'),
            ('CA_B__5876A', 'Ca B', 5876.0, 'He I 5876 Bcase'),
            ('HE_1__7281A', 'He 1', 7281.0, 'He I 7281'),
            ('HE_1__7065A', 'He 1', 7065.0, 'He I 7065'),
            ('HE_1__4471A', 'He 1', 4471.0, 'He I 4471'),
            ('CA_B__4471A', 'Ca B', 4471.0, 'He I 4471 Bcase'),
            ('HE_1__6678A', 'He 1', 6678.0, 'He I 6678'),
            ('CA_B__6678A', 'Ca B', 6678.0, 'He I 6678 Bcase'),
            ('TOTL_1083M', 'TOTL',  1.083, 'He I 1.083'),
            ('HE_2__1640A', 'He 2', 1640.0, 'He I 1640'),
            ('HE_2__4686A', 'He 2', 4686.0, 'He II 4686'),
            ('C__1__8727A', 'C  1', 8727.0, '[C I] 8727'),
            ('TOTL__9850A', 'TOTL', 9850.0, '[C I] 9850'),
            ('C_IC__9850A', 'C Ic', 9850.0, '[C I] 9850 coll'),
            ('TOTL__2326A', 'TOTL', 2326.0, 'C II] 2326+'),
            ('C__2__1335A', 'C  2', 1335.0, 'C II 1335'),
            ('C__2__1761A', 'C  2', 1761.0, 'C II 1761'),
            ('TOTL__6580A', 'TOTL', 6580.0, '[C II] 6580'),
            ('C__2__4267A', 'C  2', 4267.0, 'C II 4267'),
            ('C__2_1576M', 'C  2', 157.6, '[C II] 157.6m'),
            ('C__3_9770A', 'C  3', 977.0, '[C III] 977'),
            ('C__3__1907A', 'C  3', 1907.0, '[C III] 1907'),
            ('C__3__1910A', 'C  3', 1910.0, '[C III] 1910'),
            ('C__3__4649A', 'C  3', 4649.0, 'C III 4649'),
            ('C__3__2297A', 'C  3', 2297.0, 'C III 2297'),
            ('TOTL__1549A', 'TOTL', 1549.0, 'C IV 1549 totl'),
            ('C__4__1549A', 'C  4', 1549.0, 'C IV 1549 rec'),
            ('C__4__4659A', 'C  4', 4659.0, 'C IV 4649'),
            ('N__1__5198A', 'N  1', 5198.0, '[N I] 5198'),
            ('N__1__5200A', 'N  1', 5200.0, '[N I] 5200'),
            ('N__2__5755A', 'N  2', 5755.0, '[N II] 5755'),
            ('N_2R__5755A', 'N 2r', 5755.0, 'N II 5755 rec'),
            ('N__2__6548A', 'N  2', 6548.0, '[N II] 6548'),
            ('N__2__6584A', 'N  2', 6584.0, '[N II] 6584'),
            ('N__2__2141A', 'N  2', 2141.0, 'N II 2141'),
            ('N__2__4239A', 'N  2', 4239.0, 'N II 4239'),
            ('N__2__4041A', 'N  2', 4041.0, 'N II 4041'),
            ('TOTL__5679A', 'TOTL', 5679.0, 'N II 5679 totl'),
            ('N__2_1217M', 'N  2', 121.7, '[N II] 121.7m'),
            ('N__2_2054M', 'N  2', 205.4, '[N II] 205.4m'),
            ('N__3_5721M', 'N  3', 57.21, '[N III] 57.21m'),
            ('N__3__4641A', 'N  3', 4641.0, 'N III 4641'),
            ('TOTL__1750A', 'TOTL', 1750.0, 'N III] 1750+'),
            ('N__3__4379A', 'N  3', 4379.0, 'N III 4379'),
            ('N__4__1485A', 'N  4', 1485.0, 'N IV] 1485'),
            ('N__4__1719A', 'N  4', 1719.0, 'N IV 1719'),
            ('TOTL__1240A', 'TOTL', 1240.0, '[N V] 1240 totl'),
            ('N__5__1239A', 'N  5', 1239.0, '[N V] 1239'),
            ('O__1__7773A', 'O  1', 7773.0, 'O I 7773'),
            ('O__1__6300A', 'O  1', 6300.0, '[O I] 6300'),
            ('O__1__5577A', 'O  1', 5577.0, '[O I] 5577'),
            ('O__1_6317M', 'O  1', 63.17, '[O I] 63.17m'),
            ('O__1_1455M', 'O  1', 145.5, '[O I] 145.5m'),
            ('O_II__3726A', 'O II', 3726.0, '[O II] 3726'),
            ('O_II__3729A', 'O II', 3729.0, '[O II] 3729'),
            ('O_II__7323A', 'O II', 7323.0, '[O II] 7323'),
            ('O_II__7332A', 'O II', 7332.0, '[O II] 7332'),
            ('O_2R__3726A', 'O 2r', 3726.0, 'O II 3726 rec'),
            ('O_2R__3729A', 'O 2r', 3729.0, 'O II 3729 rec'),
            ('O_2R__7323A', 'O 2r', 7323.0, 'O II 7323 rec'),
            ('O_2R__7332A', 'O 2r', 7332.0, 'O II 7332 rec'),
            ('TOTL__3727A', 'TOTL', 3727.0, '[O II] 3727+'),
            ('TOTL__7325A', 'TOTL', 7325.0, '[O II] 7325+'),
            ('O_II__2471A', 'O II', 2471.0, '[O II] 2471+'),
            ('O__2__4152A', 'O  2', 4152.0, 'O II 4152'),
            ('TOTL__4341A', 'TOTL', 4341.0, 'O II 4341'),
            ('O__2__4651A', 'O  2', 4651.0, 'O II 4651'),
            ('O_2R__4651A', 'O 2r', 4651.0, 'O II 4651+'),
            ('TOTL__4363A', 'TOTL', 4363.0, '[O III] 4363'),
            ('REC___4363A', 'Rec ', 4363.0, 'O III 4363 rec'),
            ('O__3__4959A', 'O  3', 4959.0, '[O III] 4959'),
            ('O__3__5007A', 'O  3', 5007.0, '[O III] 5007'),
            ('O__3_5180M', 'O  3', 51.8, '[O III] 51.8m'),
            ('O__3_8833M', 'O  3', 88.33, '[O III] 88.33m'),
            ('TOTL__1665A', 'TOTL', 1665.0, '[O III] 1665+'),
            ('TOTL__1402A', 'TOTL', 1402.0, 'O IV] 1402+'),
            ('O__4__1342A', 'O  4', 1342.0, 'O IV 1342'),
            ('O__4_2588M', 'O  4', 25.88, '[O IV] 25.88m'),
            ('TOTL__1218A', 'TOTL', 1218.0, 'O V] 1218+'),
            ('O__5__1216A', 'O  5', 1216.0, '[O V] 1216'),
            ('NE_2_1281M', 'Ne 2', 12.81, '[Ne II] 12.81m'),
            ('NE_3__3869A', 'Ne 3', 3869.0, '[Ne III] 3869'),
            ('NE_3__3968A', 'Ne 3', 3968.0, '[Ne III] 3968'),
            ('NE_3_1555M', 'Ne 3', 15.55, '[Ne III] 15.55m'),
            ('NE_3_3601M', 'Ne 3', 36.01, '[Ne III] 36.01m'),
            ('NE_3__1815A', 'Ne 3', 1815.0, '[Ne III] 1815'),
            ('NE_4__1602A', 'Ne 4', 1602.0, '[Ne IV] 1602'),
            ('NE_4__2424A', 'Ne 4', 2424.0, '[Ne IV] 2424'),
            ('NE_4__4720A', 'Ne 4', 4720.0, '[Ne IV] 4720+'),
            ('NE_5__3426A', 'Ne 5', 3426.0, '[Ne V] 3426'),
            ('NE_5__3346A', 'Ne 5', 3346.0, '[Ne V] 3346'),
            ('NE_5__2976A', 'Ne 5', 2976.0, '[Ne V] 2976'),
            ('NE_5_2431M', 'Ne 5', 24.31, '[Ne V] 24.31m'),
            ('NE_5_1432M', 'Ne 5', 14.32, '[Ne V] 14.32m'),
            ('TOTL__2798A', 'TOTL', 2798.0, '[Mg II] 2798+'),
            ('SI_2_3481M', 'Si 2', 34.81, '[Si II] 34.81m'),
            ('SI_2__2334A', 'Si 2', 2334.0, '[Si II] 2334'),
            ('SI_3__1892A', 'Si 3', 1892.0, '[Si III] 1892'),
            ('SI_4__1394A', 'Si 4', 1394.0, '[Si IV] 1394'),
            ('S_II__4070A', 'S II', 4070.0, '[S II] 4070'),
            ('S_II__4078A', 'S II', 4078.0, '[S II] 4078'),
            ('S_II__6731A', 'S II', 6731.0, '[S II] 6731'),
            ('S_II__6716A', 'S II', 6716.0, '[S II] 6716'),
            ('S_II_1029M', 'S II', 1.029, '[S II 1.029m'),
            ('S_II_1034M', 'S II', 1.034, '[S II] 1.034m'),
            ('S_II_1032M', 'S II', 1.032, '[S II] 1.032m'),
            ('S_II_1037M', 'S II', 1.037, '[S II] 1.037m'),
            ('S__3__6312A', 'S  3', 6312.0, '[S III] 6312'),
            ('S__3__9532A', 'S  3', 9532.0, '[S III] 9532'),
            ('S__3__9069A', 'S  3', 9069.0, '[S III] 9069'),
            ('S__3_1867M', 'S  3', 18.67, '[S III] 18.67m'),
            ('S__3_3347M', 'S  3', 33.47, '[S III] 33.47m'),
            ('S__4_1051M', 'S  4', 10.51, '[S IV] 10.51m'),
            ('S__4__1398A', 'S  4', 1398.0, '[S IV] 1398'),
            ('CL_2__8579A', 'Cl 2', 8579.0, '[Cl II] 8579'),
            ('CL_2__9124A', 'Cl 2', 9124.0, '[Cl II] 9124'),
            ('CL_2__6162A', 'Cl 2', 6162.0, '[Cl II] 6162'),
            ('CL_2_1440M', 'Cl 2', 14.4, '[Cl II] 14.40m'),
            ('CL_3__8552A', 'Cl 3', 8552.0, '[Cl III] 8552'),
            ('TOTL__8494A', 'TOTL', 8494.0, '[Cl III] 8494+'),
            ('CL_3__5538A', 'Cl 3', 5538.0, '[Cl III] 5538'),
            ('CL_3__5518A', 'Cl 3', 5518.0, '[Cl III] 5518'),
            ('CL_4__7532A', 'Cl 4', 7532.0, '[Cl IV] 7532'),
            ('CL_4_2040M', 'Cl 4', 20.40, '[Cl IV] 20.40m'),
            ('CL_4_1170M', 'Cl 4', 11.70, '[Cl IV] 22.70m'),
            ('AR_2_6980M', 'Ar 2', 6.98, '[Ar II] 6.98m'),
            ('AR_3__7135A', 'Ar 3', 7135.0, '[Ar III] 7135'),
            ('AR_3__7751A', 'Ar 3', 7751.0, '[Ar III] 7751'),
            ('AR_3__5192A', 'Ar 3', 5192.0, '[Ar III] 5192'),
            ('AR_3_9000M', 'Ar 3', 9.0, '[Ar III] 9.00m'),
            ('AR_3_2183M', 'Ar 3', 21.83, '[Ar III] 21.83m'),
            ('AR_4__7171A', 'Ar 4', 7171.0, '[Ar IV] 7171'),
            ('AR_4__4711A', 'Ar 4', 4711.0, '[Ar IV] 4711'),
            ('AR_4__4740A', 'Ar 4', 4740.0, '[Ar IV] 4740'),
            ('AR_5__7005A', 'Ar 5', 7005.0, '[Ar V] 7005'),
            ('AR_5_1310M', 'Ar 5', 13.1, '[Ar V] 13.1m'),
            ('AR_5_8000M', 'Ar 5', 8.0, '[Ar V] 8.00m'),
            ('FE_2__8617A', 'Fe 2', 8617.0, '[Fe II] 8617'),
            ('FE_3__4608A', 'Fe 3', 4608.0, '[Fe III] 4608'),
            ('FE_3__4668A', 'Fe 3', 4668.0, '[Fe III] 4668'),
            ('FE_3__4659A', 'Fe 3', 4659.0, '[Fe III] 4659'),
            ('FE_3__4702A', 'Fe 3', 4702.0, '[Fe III] 4702'),
            ('FE_3__4734A', 'Fe 3', 4734.0, '[Fe III] 4734'),
            ('FE_3__4881A', 'Fe 3', 4881.0, '[Fe III] 4881'),
            ('FE_3__5271A', 'Fe 3', 5271.0, '[Fe III] 5271'),
            ('FE_3__4755A', 'Fe 3', 4755.0, '[Fe III] 4755'),
            ('FE_4__2836A', 'Fe 4', 2836.0, '[Fe IV] 2836'),
            ('FE_6__5177A', 'Fe 6', 5177.0, '[Fe VI] 5177'),
            ('FE_7__4894A', 'Fe 7', 4894.0, '[Fe VII] 4894'),
            ('FE_7__5721A', 'Fe 7', 5721.0, '[Fe VII] 5721'),
            ('FE_7__4989A', 'Fe 7', 4989.0, '[Fe VII] 4989'),
            ('FE_7__6087A', 'Fe 7', 6087.0, '[Fe VII] 6087'),
            ('FE_7__5277A', 'Fe 7', 5277.0, '[Fe VII] 5277'),
            ('F12__1200M', 'F12', 12.0, 'IRAS 12m'),
            ('F25__2500M', 'F25', 25.0, 'IRAS 25m'),
            ('F60__6000M', 'F60', 60.0, 'IRAS 60m'),
            ('F100_1000M', 'F100', 100.0, 'IRAS 100m'),
            ('MIPS_2400M', 'MIPS', 24.0, 'MIPS 24m'),
            ('MIPS_7000M', 'MIPS', 70.0, 'MIPS 70m'),
            ('MIPS_1600M', 'MIPS', 160., 'MIPS 160m'),
            ('IRAC_3600M', 'IRAC', 3.6, 'IRAC 3.6m'),
            ('IRAC_4500M', 'IRAC', 4.5, 'IRAC 4.5m'),
            ('IRAC_5800M', 'IRAC', 5.8, 'IRAC 5.8m'),
            ('IRAC_8000M', 'IRAC', 8.0, 'IRAC 8.0m'),
             ]
lines_list = [
('BAC__364600A', 'Bac ', 3646.0, 'Bac  3646.0A'),
('COUT_364600A', 'cout', 3646.0, 'cout 3646.0A'),
('CREF_364600A', 'cref', 3646.0, 'cref 3646.0A'),
('H__1_486133A', 'H  1', 4861.33, 'H  1 4861.33A'),
('CA_B_486133A', 'Ca B', 4861.33, 'Ca B 4861.33A'),
('H__1_656281A', 'H  1', 6562.81, 'H  1 6562.81A'),
('CA_B_656281A', 'Ca B', 6562.81, 'Ca B 6562.81A'),
('H__1_434046A', 'H  1', 4340.46, 'H  1 4340.46A'),
('CA_B_434046A', 'Ca B', 4340.46, 'Ca B 4340.46A'),
('H__1_388905A', 'H  1', 3889.05, 'H  1 3889.05A'),
('CA_B_388905A', 'Ca B', 3889.05, 'Ca B 3889.05A'),
('H__1_121567A', 'H  1', 1215.67, 'H  1 1215.67A'),
('CA_B_121567A', 'Ca B', 1215.67, 'Ca B 1215.67A'),
('H__1_187510M', 'H  1', 1.87510, 'H  1 1.87510m'),
('CA_B_187510M', 'Ca B', 1.87510, 'Ca B 1.87510m'),
('H__1_128180M', 'H  1', 1.28180, 'H  1 1.28180m'),
('CA_B_128180M', 'Ca B', 1.28180, 'Ca B 1.28180m'),
('H__1_405113M', 'H  1', 4.05113, 'H  1 4.05113m'),
('CA_B_405113M', 'Ca B', 4.05113, 'Ca B 4.05113m'),
('H__1_262513M', 'H  1', 2.62513, 'H  1 2.62513m'),
('CA_B_262513M', 'Ca B', 2.62513, 'Ca B 2.62513m'),
('H__1_745777M', 'H  1', 7.45777, 'H  1 7.45777m'),
('CA_B_745777M', 'Ca B', 7.45777, 'Ca B 7.45777m'),
('H__1_123684M', 'H  1', 12.3684, 'H  1 12.3684m'),
('CA_B_123684M', 'Ca B', 12.3684, 'Ca B 12.3684m'),
('H__1_190565M', 'H  1', 19.0565, 'H  1 19.0565m'),
('CA_B_190565M', 'Ca B', 19.0565, 'Ca B 19.0565m'),
('H__1_276210M', 'H  1', 276.210, 'H  1 276.210m'),
('CA_B_276210M', 'Ca B', 276.210, 'Ca B 276.210m'),
('H__1_518618M', 'H  1', 518.618, 'H  1 518.618m'),
('CA_B_518618M', 'Ca B', 518.618, 'Ca B 518.618m'),
('H__1_590935M', 'H  1', 590.935, 'H  1 590.935m'),
('CA_B_590935M', 'Ca B', 590.935, 'Ca B 590.935m'),
('HE_1_587564A', 'He 1', 5875.64, 'He 1 5875.64A'),
('CA_B_587564A', 'Ca B', 5875.64, 'Ca B 5875.64A'),
('HE_1_728135A', 'He 1', 7281.35, 'He 1 7281.35A'),
('CA_B_728135A', 'Ca B', 7281.35, 'Ca B 7281.35A'),
('HE_1_706522A', 'He 1', 7065.22, 'He 1 7065.22A'),
('CA_B_706522A', 'Ca B', 7065.22, 'Ca B 7065.22A'),
('HE_1_447149A', 'He 1', 4471.49, 'He 1 4471.49A'),
('CA_B_447149A', 'Ca B', 4471.49, 'Ca B 4471.49A'),
('HE_1_667815A', 'He 1', 6678.15, 'He 1 6678.15A'),
('CA_B_667815A', 'Ca B', 6678.15, 'Ca B 6678.15A'),
('HE_1_388863A', 'He 1', 3888.63, 'He 1 3888.63A'),
('CA_B_388863A', 'Ca B', 3888.63, 'Ca B 3888.63A'),
('HE_1_108303M', 'He 1', 1.08303, 'He 1 1.08303m'),
('CA_B_108303M', 'Ca B', 1.08303, 'He 1B 1.08303m'),
('TOTL_108303M', 'TOTL', 1.08303, 'He 1 1.08303m+'),
('HE_1_205813M', 'He 1', 2.05813, 'He 1 2.05813m'),
('CA_B_205813M', 'Ca B', 2.05813, 'He 1B 2.058133m'),
('HE_2_164043A', 'He 2', 1640.43, 'He 2 1640.43A'),
('CA_B_164043A', 'Ca B', 1640.43, 'Ca B 1640.43A'),
('HE_2_468564A', 'He 2', 4685.64, 'He 2 4685.64A'),
('CA_B_468564A', 'Ca B', 4685.64, 'Ca B 4685.64A'),
('HE_2_101233M', 'He 2', 1.01233, 'He 2 1.01233m'),
('CA_B_101233M', 'Ca B', 1.01233, 'Ca B 1.01233m'),
('C__1_872713A', 'C  1', 8727.13, 'C  1 8727.13A'),
('C__1_985026A', 'C  1', 9850.26, 'C  1 9850.26A'),
('C_1R_985000A', 'C 1R', 9850.00, 'C 1R 9850.00A'),
('BLND_232600A', 'BLND', 2326.0, 'C 2 2326.0A+'),
('BLND_133500A', 'BLND', 1335.0, 'C 2 1335.0A+'),
('C_2R_133500A', 'C 2R', 1335.0, 'C 2R 1335.0A'),
('C__2_176100A', 'C  2', 1761.0, 'C  2 1761.0A'),
('BLND_658000A', 'BLND', 6580.0, 'C  2 6580.0A+'),
('C_2R_658000A', 'C 2R', 6580.0, 'C 2R 6580.0A'),
('C__2_426700A', 'C  2', 4267.0, 'C  2 4267.0A'),
('C__2_157636M', 'C  2', 157.636, 'C  2 157.636m'),
('C__3_977000A', 'C  3', 977.0, 'C  3 977.0A'),
('C__3_190668A', 'C  3', 1906.68, 'C  3 1906.68A'),
('C__3_190873A', 'C  3', 1908.73, 'C  3 1908.73A'),
('BLND_190900A', 'Blnd', 1909.0, 'C  3 1909.0A+'),
('C_3R_190900A', 'C 3R', 1909.0, 'C 3R 1909.0A'),
('C__3_464900A', 'C  3', 4649.0, 'C  3 4649.0A'),
('C__3_406900A', 'C  3', 4069.0, 'C  3 4069.0A'),
('C__3_229690A', 'C  3', 2296.9, 'C  3 2296.9A'),
('BLND_154900A', 'BLND', 1549.0, 'C  4 1549.0A+'),
('C_4R_154900A', 'C 4R', 1549.0, 'C 4R 1549.0A'),
('C__4_465900A', 'C  4', 4659.0, 'C  4 4659.0A'),
('N__1_519790A', 'N  1', 5197.9, 'N  1 5197.9A'),
('N__1_520026A', 'N  1', 5200.26, 'N  1 5200.26A'),
('BLND_519900A', 'Blnd', 5199.0, 'N  1 5199.0A+'),
('N_1R_519900A', 'N 1R', 5199.0, 'N 1R 5199.0A'),
('BLND_575500A', 'BLND', 5755.0, 'N  2 5755.0A+'),
('N_2R_575500A', 'N 2R', 5755.0, 'N 2R 5755.0A'),
('N__2_500500A', 'N  2', 5005.0, 'N 2R 5005.0A'),
('N__2_654805A', 'N  2', 6548.05, 'N  2 6548.05A'),
('N__2_658345A', 'N  2', 6583.45, 'N  2 6583.45A'),
('BLND_214100A', 'Blnd', 2141.0, 'N 2 2141.0A'),
('N__2_214278A', 'N  2', 2142.78, 'N  2 2142.78A'),
('N__2_404100A', 'N  2', 4041.0, 'N  2 4041.0A'),
('N__2_121767M', 'N  2', 121.767, 'N  2 121.767m'),
('N__2_205244M', 'N  2', 205.244, 'N  2 205.244m'),
('N_2R_566663A_PN', 'N 2R', 5666.63, 'N 2R 5666.63A PN'),
('N_2R_567602A_PN', 'N 2R', 5676.02, 'N 2R 5676.02A PN'),
('N_2R_567956A_PN', 'N 2R', 5679.56, 'N 2R 5679.56A PN'),
('N_2R_568621A_PN', 'N 2R', 5686.21, 'N 2R 5686.21A PN'),
('N_2R_571077A_PN', 'N 2R', 5710.77, 'N 2R 5710.77A PN'),
('N_2R_500515A_PN', 'N 2R', 5005.15, 'N 2R 5005.15A PN'),
('N_2R_500114A_PN', 'N 2R', 5001.14, 'N 2R 5001.14A PN'),
('N_2R_500148A_PN', 'N 2R', 5001.48, 'N 2R 5001.48A PN'),
('N__3_573238M', 'N  3', 57.3238, 'N  3 57.3238m'),
('BLND_175000A', 'BLND', 1750.0, 'N  3 1750.0A+'),
('N__3_437900A', 'N  3', 4379.0, 'N  3 4379.0A'),
('BLND_148600A', 'BLND', 1486.0, 'N  4 1486.0A+'),
('N__4_171855A', 'N  4', 1718.55, 'N  4 1718.55A'),
('N__5_124280A', 'N  5', 1242.80, 'N  5 1242.80A'), 
('N__5_123882A', 'N  5', 1238.82, 'N  5 1238.82A'),
('O__1_777300A', 'O  1', 7773.0, 'O  1 7773.0A'),
('O__1_630030A', 'O  1', 6300.30, 'O  1 6300.3A'),
('O__1_557734A', 'O  1', 5577.34, 'O  1 5577.34A'),
('O__1_631679M', 'O  1', 63.1679, 'O  1 63.1679m'),
('O__1_145495M', 'O  1', 145.495, 'O  1 145.495m'),
('O__2_372603A', 'O  2', 3726.03, 'O  2 3726.03A'),
('O__2_372881A', 'O  2', 3728.81, 'O  2 3728.81A'),
('BLND_732300A', 'Blnd', 7323.0, 'O  2 7323.0A+'),
('BLND_733200A', 'Blnd', 7332.0, 'O  2 7332.0A+'),
('O_2R_372600A', 'O 2R', 3726.0, 'O 2R 3726.0A'),
('O_2R_372900A', 'O 2R', 3729.0, 'O 2R 3729.0A'),
('O_2R_732300A', 'O 2R', 7323.0, 'O 2R 7323.0A'),
('O_2R_733200A', 'O 2R', 7332.0, 'O 2R 7332.0A'),
('BLND_372700A', 'BLND', 3727.0, 'O  2 3727.0A+'),
('BLND_732500A', 'BLND', 7325.0, 'O  2 7325.0A+'),
('BLND_247100A', 'BLND', 2471.0, 'O  2 2471.0A+'),
('O__2_415200A', 'O  2', 4152.0, 'O  2 4152.0A'),
('BLND_434100A', 'BLND', 4341.0, 'O  2 4341.0A+'),
('O__2_465100A', 'O  2', 4651.0, 'O  2 4651.0A'),
('O_2R_465100A', 'O 2R', 4651.0, 'O 2R 4651.0A'),
('O_2R_463886A_PN', 'O 2R', 4638.86, 'O 2R 4638.86A PN'),
('O_2R_464181A_PN', 'O 2R', 4641.81, 'O 2R 4641.81A PN'),
('O_2R_464913A_PN', 'O 2R', 4649.13, 'O 2R 4649.13A PN'),
('O_2R_465084A_PN', 'O 2R', 4650.84, 'O 2R 4650.84A PN'),
('O_2R_466163A_PN', 'O 2R', 4661.63, 'O 2R 4661.63A PN'),
('O_2R_467373A_PN', 'O 2R', 4673.73, 'O 2R 4673.73A PN'),
('O_2R_467623A_PN', 'O 2R', 4676.23, 'O 2R 4676.23A PN'),
('O_2R_469635A_PN', 'O 2R', 4696.35, 'O 2R 4696.35A PN'),
('O_2R_406988A_PN', 'O 2R', 4069.88, 'O 2R 4069.88A PN'),
('O_2R_407215A_PN', 'O 2R', 4072.15, 'O 2R 4072.15A PN'),
('O_2R_407586A_PN', 'O 2R', 4075.86, 'O 2R 4075.86A PN'),
('O_2R_407884A_PN', 'O 2R', 4078.84, 'O 2R 4078.84A PN'),
('O_2R_408511A_PN', 'O 2R', 4085.11, 'O 2R 4085.11A PN'),
('O_2R_409293A_PN', 'O 2R', 4092.93, 'O 2R 4092.93A PN'),
('BLND_436300A', 'BLND', 4363.0, 'O 33 4363.0A'),
('O_3R_436300A', 'O 3R', 4363.0, 'O 3R 4363.0A'),
('O__3_495891A', 'O  3', 4958.91, 'O  3 4958.91A'),
('O__3_500684A', 'O  3', 5006.84, 'O  3 5006.84A'),
('O__3_518004M', 'O  3', 51.8004, 'O  3 51.8004m'),
('O__3_883323M', 'O  3', 88.3323, 'O  3 88.3323m'),
('O__3_166081A', 'O  3', 1660.81, 'O  3 1660.81A'),
('BLND_166600A', 'BLND', 1666.0, 'O  3 1666.0A+'),
('BLND_140200A', 'BLND', 1402.0, 'O  4 1402.0A+'),
('O__4_258832M', 'O  4', 25.8832, 'O  4 25.8832m'),
('O__4_463200A', 'O  4', 4632.00, 'O  4 4632.00A'),
('BLND_121800A', 'BLND', 1218.00, 'O 5 1218.0A+'),
('O__6_103191A', 'O  6', 1031.91, '[O VI] 1032A'),
('O__6_103762A', 'O  6', 1037.62, '[O VI] 1038A'),
('F__2_478945A', 'F  2', 4789.45, 'F  2 4789.45A'),
('F__4_399692A', 'F  4', 3996.92, 'F  4 3996.92A'),
('F__4_405990A', 'F  4', 4059.9, 'F  4 4059.9A'),
('NE_2_128101M', 'Ne 2', 12.8101, 'Ne 2 12.8101m'),
('NE_3_386876A', 'Ne 3', 3868.76, 'Ne 3 3868.76A'),
('NE_3_396747A', 'Ne 3', 3967.47, 'Ne 3 3967.47A'),
('NE_3_181456A', 'Ne 3', 1814.56, 'Ne 3 1814.56A'),
('NE_3_401168A', 'Ne 3', 4011.68, 'Ne 3 4011.68A'),
('NE_3_155509M', 'Ne 3', 15.5509, 'Ne 3 15.5509m'),
('NE_3_360036M', 'Ne 3', 36.0036, 'Ne 3 36.0036m'),
('NE_4_160161A', 'Ne 4', 1601.61, 'Ne 4 1601.61A'),
('NE_4_160145A', 'Ne 4', 1601.45, 'Ne 4 1601.45A'),
('BLND_242400A', 'BLND', 2424.00, 'Ne 4 2424.0A+'),
('BLND_472000A', 'BLND', 4720.00, 'Ne 4 4720.0A+'),
('NE_5_334599A', 'Ne 5', 3345.99, 'Ne 5 3345.99A'),
('NE_5_342603A', 'Ne 5', 3426.03, 'Ne 5 3426.03A'),
('NE_5_157476A', 'Ne 5', 1574.76, 'Ne 5 1574.76A'),
('NE_5_297320A', 'Ne 5', 2973.20, 'Ne 5 2973.2A'),
('NE_5_242065M', 'Ne 5', 24.2065, 'Ne 5 24.2065m'),
('NE_5_143228M', 'Ne 5', 14.3228, 'Ne 5 14.3228m'),
('NE_6_764318M', 'Ne 6', 7.64318, 'Ne 6 7.64318m'),
('NA_3_731706M', 'Na 3', 7.31706, 'Na 3 7.31706m'),
('MG_2_279553A', 'Mg 2', 2795.53, 'Mg 2 2795.53A'),
('MG_2_280271A', 'Mg 2', 2802.71, 'Mg 2 2802.71A'),
('MG_4_448712M', 'Mg 4', 4.48712, 'Mg 4 4.48712m'),
('MG_5_560700M', 'Mg 5', 5.60700, 'Mg 5 5.60700m'),
('MG_5_135464M', 'Mg 5', 13.5464, 'Mg 5 13.5464m'),
('MG_5_278276A', 'Mg 5', 2782.76, 'Mg 5 2782.76A'),
('MG_7_550177M', 'Mg 7', 5.50177, 'Mg 7 5.50177m'),
('AL_2_266915A', 'Al 2', 2669.15, 'Al 2 2669.15A'),
('AL_2_266035A', 'Al 2', 2660.35, 'Al 2 2660.35A'),
('BLND_186000A', 'Blnd', 1860.00, 'Al 3 1860.0A+'),
('SI_2_348046M', 'Si 2', 34.8046, 'Si 2 34.8046m'),
('BLND_233500A', 'BLND', 2335.00, 'Si 2 2335.0A+'),
('SI_3_189203A', 'Si 3', 1892.03, 'Si 3 1892.03A'),
('SI_3_188271A', 'Si 3', 1882.71, 'Si 3 1882.71A'),
('SI_4_139375A', 'Si 4', 1393.75, 'Si 4 1393.75A'),
('SI_6_196247M', 'Si 6', 1.96247, 'Si 6 1.96247m'),
('SI_7_248071M', 'Si 7', 2.48071, 'Si 7 2.48071m'),
('SI_7_651288M', 'Si 7', 6.51288, 'Si 7 6.51288m'),
('S__2_406860A', 'S  2', 4068.60, 'S  2 4068.6A'),
('S__2_407635A', 'S  2', 4076.35, 'S  2 4076.35A'),
('S__2_673082A', 'S  2', 6730.82, 'S  2 6730.82A'),
('S__2_671644A', 'S  2', 6716.44, 'S  2 6716.44A'),
('S__2_102867M', 'S  2', 1.02867, 'S  2 1.02867m'),
('S__2_103364M', 'S  2', 1.03364, 'S  2 1.03364m'),
('S__2_103205M', 'S  2', 1.03205, 'S  2 1.03205m'),
('S__2_103705M', 'S  2', 1.03705, 'S  2 1.03705m'),
('S__3_631206A', 'S  3', 6312.06, 'S  3 6312.06A'),
('S__3_953062A', 'S  3', 9530.62, 'S  3 9530.62A'),
('S__3_906862A', 'S  3', 9068.62, 'S  3 9068.62A'),
('S__3_187078M', 'S  3', 18.7078, 'S  3 18.7078m'),
('S__3_334704M', 'S  3', 33.4704, 'S  3 33.4704m'),
('S__4_105076M', 'S  4', 10.5076, 'S  4 10.5076m'),
('S__4_139804A', 'S  4', 1398.04, 'S  4 1398.04A'),
('BLND_140600A', 'BLND', 1406.00, 'S  4 1406A+'),
('S__5_119914A', 'S  5', 1199.14, 'S  5 1199.14A'),
('S__5_118828A', 'S  5', 1188.28, 'S  5 1188.28A'),
('CL_2_857870A', 'Cl 2', 8578.70, 'Cl 2 8578.70A'),
('CL_2_912360A', 'Cl 2', 9123.60, 'Cl 2 9123.60A'),
('CL_2_616184A', 'Cl 2', 6161.84, 'Cl 2 6161.84A'),
('CL_2_143639M', 'Cl 2', 14.3639, 'Cl 2 14.3639m'),
('CL_2_332721M', 'Cl 2', 33.2721, 'Cl 2 33.2721m'),
('CL_3_553787A', 'Cl 3', 5537.87, 'Cl 3 5537.87A'),
('CL_3_551771A', 'Cl 3', 5517.71, 'Cl 3 5517.71A'),
('CL_3_335317A', 'Cl 3', 3353.17, 'Cl 3 3353.17A'),
('CL_3_334280A', 'Cl 3', 3342.80, 'Cl 3 3342.80A'),
('CL_3_850001A', 'Cl 3', 8500.01, 'Cl 3 8500.01A'),
('CL_3_854796A', 'Cl 3', 8547.96, 'Cl 3 8547.96A'),
('CL_3_843366A', 'Cl 3', 8433.66, 'Cl 3 8433.66A'),
('CL_3_848086A', 'Cl 3', 8480.86, 'Cl 3 8480.86A'),
('BLND_849400A', 'BLND', 8494.00, 'Cl 3 8494.0A+'),
('CL_4_753054A', 'Cl 4', 7530.54, 'Cl 4 7530.54A'),
('CL_4_804562A', 'Cl 4', 8045.62, 'Cl 4 8045.62A'),
('CL_4_203197M', 'Cl 4', 20.3197, 'Cl 4 20.3197m'),
('CL_4_117629M', 'Cl 4', 11.7629, 'Cl 4 11.7629m'),
('CL_5_670733M', 'Cl 5', 6.70733, 'Cl 5 6.70733m'),
('AR_2_698337M', 'Ar 2', 6.98337, 'Ar 2 6.98337m'),
('AR_3_713579A', 'Ar 3', 7135.79, 'Ar 3 7135.79A'),
('AR_3_775111A', 'Ar 3', 7751.11, 'Ar 3 7751.11A'),
('AR_3_519182A', 'Ar 3', 5191.82, 'Ar 3 5191.82A'),
('AR_3_310918A', 'Ar 3', 3109.18, 'Ar 3 3109.18A'),
('AR_3_898898M', 'Ar 3', 8.98898, 'Ar 3 8.98898m'),
('AR_3_218253M', 'Ar 3', 21.8253, 'Ar 3 21.8253m'),
('AR_4_717070A', 'Ar 4', 7170.70, 'Ar 4 7170.70A'),
('AR_4_471126A', 'Ar 4', 4711.26, 'Ar 4 4711.26A'),
('AR_4_474012A', 'Ar 4', 4740.12, 'Ar 4 4740.12A'),
('AR_4_285366A', 'Ar 4', 2853.66, 'Ar 4 2853.66A'),
('AR_4_286822A', 'Ar 4', 2868.22, 'Ar 4 2868.22A'),
('AR_5_700583A', 'Ar 5', 7005.83, 'Ar 5 7005.83A'),
('AR_5_130985M', 'Ar 5', 13.0985, 'Ar 5 13.0985m'),
('AR_5_789971M', 'Ar 5', 7.89971, 'Ar 5 7.89971m'),
('AR_5_643512A', 'Ar 5', 6435.12, 'Ar 5 6435.12A'),
('AR_6_452800M', 'Ar 6', 4.52800, 'Ar 6 4.52800m'),
('K__6_560244A', 'K  6', 5602.44, 'K  6 5602.44A'),
('K__6_622857A', 'K  6', 6228.57, 'K  6 6228.57A'),
('K__6_882061M', 'K  6', 8.82061, 'K  6 8.82061m'),
('K__6_557324M', 'K  6', 5.57324, 'K  6 5.57324m'),
('CA_2_729147A', 'Ca 2', 7291.47, 'K  6 7291.47A'),
('CA_2_732389A', 'Ca 2', 7323.89, 'Ca 2 7323.89A'),
('CA_2_866214A', 'Ca 2', 8662.14, 'Ca 2 8662.14A'),
('CA_2_849802A', 'Ca 2', 8498.02, 'Ca 2 8498.02A'),
('CA_2_854209A', 'Ca 2', 8542.09, 'Ca 2 8542.09A'),
('FE_2_259811M', 'Fe 2', 25.9811, 'Fe 2 25.9811m'),
('FE_2_533881M', 'Fe 2', 5.33881, 'Fe 2 5.33881m'),
('FE_2_411394M', 'Fe 2', 4.11394, 'Fe 2 4.11394m'),
('FE_2_353394M', 'Fe 2', 35.3394, 'Fe 2 35.3394m'),
('FE_2_861695A', 'Fe 2', 8616.95, 'Fe 2 8616.95A'),
('FE_3_460711A', 'Fe 3', 4607.11, 'Fe 3 4607.11A'),
('FE_3_466694A', 'Fe 3', 4666.94, 'Fe 3 4666.94A'),
('FE_3_465801A', 'Fe 3', 4658.01, 'Fe 3 4658.01A'),
('FE_3_470162A', 'Fe 3', 4701.62, 'Fe 3 4701.62A'),
('FE_3_473384A', 'Fe 3', 4733.84, 'Fe 3 4733.84A'),
('FE_3_488112A', 'Fe 3', 4881.12, 'Fe 3 4881.12A'),
('FE_3_527040A', 'Fe 3', 5270.40, 'Fe 3 5270.40A'),
('FE_3_475464A', 'Fe 3', 4754.64, 'Fe 3 4754.64A'),
('FE_4_283574A', 'Fe 4', 2835.74, 'Fe 4 2835.74A'),
('FE_6_514576A', 'Fe 6', 5145.76, 'Fe 6 5145.76A'),
('FE_7_572071A', 'Fe 7', 5720.71, 'Fe 7 5720.71A'),
('FE_7_498855A', 'Fe 7', 4988.55, 'Fe 7 4988.55A'),
('FE_7_608697A', 'Fe 7', 6086.97, 'Fe 7 6086.97A'),
('FE10_637454A', 'Fe10', 6374.54, 'Fe 10 6374.54A'),
('FE11_789187A', 'Fe11', 7891.87, 'Fe 11 7891.87A'),
('F12__120000M', 'F12 ', 12.0, 'F12  12.0mu'),
('F25__250000M', 'F25 ', 25.0, 'F25  25.0mu'),
('F60__600000M', 'F60 ', 60.0, 'F60  60.0mu'),
('F100_100000M', 'F100', 100.0, 'F100 100.0mu'),
('MIPS_240000M', 'MIPS', 24.0, 'MIPS 24.0mu'),
('MIPS_700000M', 'MIPS', 70.0, 'MIPS 70.0mu'),
('MIPS_160000M', 'MIPS', 160.0, 'MIPS 160.0mu'),
('IRAC_360000M', 'IRAC', 3.6, 'IRAC 3.6mu'),
('IRAC_450000M', 'IRAC', 4.5, 'IRAC 4.5mu'),
('IRAC_580000M', 'IRAC', 5.8, 'IRAC 5.8mu'),
('IRAC_800000M', 'IRAC', 8.0, 'IRAC 8.0mu'),
('R25_119917C',  'R2.5', 119917.00, 'Radio 2.5GHz'),
('R49_616860C',  'R4.9', 61686.00, 'Radio 4.9GHz'),
('R12__249830C',  'R12',  24983.00, 'Radio 12GHz'),
('R20__149900C',  'R20',  14990.00, 'Radio 20GHz')
]

elem_list = [('HYDROGEN', 2),
             ('HELIUM', 2),
             ('LITHIUM', 3),
             ('BERYLLIUM', 4),
             ('BORON', 5),
             ('CARBON', 6),
             ('NITROGEN', 7),
             ('OXYGEN', 8),
             ('FLUORINE', 9),
             ('NEON', 10),
             ('SODIUM', 11),
             ('MAGNESIUM', 12),
             ('ALUMINIUM', 13),
             ('SILICON', 14),
             ('PHOSPHORUS', 15),
             ('SULPHUR', 16),
             ('CHLORINE', 17),
             ('ARGON', 18),
             ('POTASSIUM', 19),
             ('CALCIUM', 20),
             ('SCANDIUM', 21),
             ('TITANIUM',22),
             ('VANADIUM', 23),
             ('CHROMIUM', 24),
             ('MANGANESE', 25),
             ('IRON', 26),
             ('COBALT', 27),
             ('NICKEL', 28),
             ('COPPER', 29),
             ('ZINC', 30),
              ]            

# fields1 are in pending and tab
fields1 = """`N` bigint(20) NOT NULL AUTO_INCREMENT,
  `user` varchar(40) NOT NULL DEFAULT '',
  `date_submitted` datetime DEFAULT NULL,
  `date_running` datetime DEFAULT NULL,
  `ref` varchar(40) NOT NULL DEFAULT '',
  `file` varchar(40) NOT NULL DEFAULT '',
  `dir` varchar(80) NOT NULL DEFAULT '',
  `C_version` varchar(10) NOT NULL DEFAULT '10.00',
  `geom` varchar(10) NOT NULL DEFAULT '',
  `atm_cmd` varchar(60) NOT NULL DEFAULT '',
  `atm_file` varchar(40) NOT NULL DEFAULT '',
  `atm1` double DEFAULT NULL,
  `atm2` double DEFAULT NULL,
  `atm3` double DEFAULT NULL,
  `lumi_unit` varchar(40) NOT NULL DEFAULT '',
  `lumi` double DEFAULT NULL,
  `atm_cmd2` varchar(60) NOT NULL DEFAULT '',
  `atm_file2` varchar(40) NOT NULL DEFAULT '',
  `atm12` double DEFAULT NULL,
  `atm22` double DEFAULT NULL,
  `atm32` double DEFAULT NULL,
  `lumi_unit2` varchar(40) NOT NULL DEFAULT '',
  `lumi2` double DEFAULT NULL,
  `dens` double DEFAULT NULL,
  `dlaw1` double DEFAULT NULL,
  `dlaw2` double DEFAULT NULL,
  `dlaw3` double DEFAULT NULL,
  `dlaw4` double DEFAULT NULL,
  `dlaw5` double DEFAULT NULL,
  `dlaw6` double DEFAULT NULL,
  `dlaw7` double DEFAULT NULL,
  `dlaw8` double DEFAULT NULL,
  `dlaw9` double DEFAULT NULL,
  `radius` double DEFAULT NULL,
  `ff` double NOT NULL DEFAULT 1.,
  `iterate` int(11) NOT NULL DEFAULT 1,
  `dust_type1` varchar(40) NOT NULL DEFAULT '',
  `dust_value1` double DEFAULT NULL,
  `dust_type2` varchar(40) NOT NULL DEFAULT '',
  `dust_value2` double DEFAULT NULL,
  `dust_type3` varchar(40) NOT NULL DEFAULT '',
  `dust_value3` double DEFAULT NULL,
  `stop1` varchar(80) NOT NULL DEFAULT '',
  `stop2` varchar(80) NOT NULL DEFAULT '',
  `stop3` varchar(80) NOT NULL DEFAULT '',
  `stop4` varchar(80) NOT NULL DEFAULT '',
  `stop5` varchar(80) NOT NULL DEFAULT '',
  `stop6` varchar(80) NOT NULL DEFAULT '',
  `cloudy1` varchar(80) NOT NULL DEFAULT '',
  `cloudy2` varchar(80) NOT NULL DEFAULT '',
  `cloudy3` varchar(80) NOT NULL DEFAULT '',
  `cloudy4` varchar(80) NOT NULL DEFAULT '',
  `cloudy5` varchar(80) NOT NULL DEFAULT '',
  `cloudy6` varchar(80) NOT NULL DEFAULT '',
  `cloudy7` varchar(80) NOT NULL DEFAULT '',
  `cloudy8` varchar(80) NOT NULL DEFAULT '',
  `cloudy9` varchar(80) NOT NULL DEFAULT '',
  `com1` varchar(80) NOT NULL DEFAULT '',
  `com2` varchar(80) NOT NULL DEFAULT '',
  `com3` varchar(80) NOT NULL DEFAULT '',
  `com4` varchar(80) NOT NULL DEFAULT '',
  `com5` varchar(80) NOT NULL DEFAULT '',
  `com6` varchar(80) NOT NULL DEFAULT '',
  `com7` varchar(80) NOT NULL DEFAULT '',
  `com8` varchar(80) NOT NULL DEFAULT '',
  `com9` varchar(80) NOT NULL DEFAULT '',
  `distance` double NOT NULL DEFAULT 1,
  `N_Mass_cut` int(11) NOT NULL DEFAULT 0,
  `N_Hb_cut` int(11) NOT NULL DEFAULT 0,
  `GuessMassFrac` double NOT NULL DEFAULT 1,
  `status` int(11) DEFAULT -1,
"""

# fields2 are only in tab
fields2 ="""`DepthFrac` double NOT NULL DEFAULT 1,
  `MassFrac` double NOT NULL DEFAULT 1,
  `HbFrac` double NOT NULL DEFAULT 1,
  `rout` double NOT NULL DEFAULT 0,
  `thickness` double NOT NULL DEFAULT 0,
  `N_zones` int(11) NOT NULL DEFAULT '0',
  `CloudyEnds` varchar(180) NOT NULL DEFAULT '',
  `FirstZone` varchar(180) NOT NULL DEFAULT '',
  `LastZone` varchar(180) NOT NULL DEFAULT '',
  `CalculStop` varchar(180) NOT NULL DEFAULT '',
  `logQ` float NOT NULL DEFAULT 0,
  `logQ0` float NOT NULL DEFAULT 0,
  `logQ1` float NOT NULL DEFAULT 0,
  `logQ2` float NOT NULL DEFAULT 0,
  `logQ3` float NOT NULL DEFAULT 0,
  `logQ11.26` float NOT NULL DEFAULT 0,
  `logQ35.12` float NOT NULL DEFAULT 0,
  `logQ40.73` float NOT NULL DEFAULT 0,
  `logQ47.45` float NOT NULL DEFAULT 0,
  `logQ77.41` float NOT NULL DEFAULT 0,
  `logQ113.90` float NOT NULL DEFAULT 0,
  `logQ138.12` float NOT NULL DEFAULT 0,
  `logQ151.06` float NOT NULL DEFAULT 0,
  `logQ233.60` float NOT NULL DEFAULT 0,
  `logQ262.10` float NOT NULL DEFAULT 0,
  `logQ361.00` float NOT NULL DEFAULT 0,
  `logPhi` float NOT NULL DEFAULT 0,
  `logPhi0` float NOT NULL DEFAULT 0,
  `logPhi1` float NOT NULL DEFAULT 0,
  `logPhi2` float NOT NULL DEFAULT 0,
  `logPhi3` float NOT NULL DEFAULT 0,
  `logPhi11.26` float NOT NULL DEFAULT 0,
  `logPhi35.12` float NOT NULL DEFAULT 0,
  `logPhi40.73` float NOT NULL DEFAULT 0,
  `logPhi47.45` float NOT NULL DEFAULT 0,
  `logPhi77.41` float NOT NULL DEFAULT 0,
  `logPhi113.90` float NOT NULL DEFAULT 0,
  `logPhi138.12` float NOT NULL DEFAULT 0,
  `logPhi151.06` float NOT NULL DEFAULT 0,
  `logPhi233.60` float NOT NULL DEFAULT 0,
  `logPhi262.10` float NOT NULL DEFAULT 0,
  `logPhi361.00` float NOT NULL DEFAULT 0,
  `logU_in` float NOT NULL DEFAULT '0',
  `logU_out` float NOT NULL DEFAULT '0',
  `logU_mean` float NOT NULL DEFAULT 0,
  `THp` float NOT NULL DEFAULT 0,
  `t2_H1` float NOT NULL DEFAULT 0,
  `t2_O1` float NOT NULL DEFAULT 0,
  `t2_O2` float NOT NULL DEFAULT 0,
  `t2_O3` float NOT NULL DEFAULT 0,
  `ne_H1` float NOT NULL DEFAULT 0,
  `ne_O1` float NOT NULL DEFAULT 0,
  `ne_O2` float NOT NULL DEFAULT 0,
  `ne_O3` float NOT NULL DEFAULT 0,  
  `H_mass` float NOT NULL DEFAULT 0,
  `H1_mass` float NOT NULL DEFAULT 0,
  `nH_mean` float NOT NULL DEFAULT 0,
  `nH_in` float NOT NULL DEFAULT 0,
  `nH_out` float NOT NULL DEFAULT 0,
  `Hb_SB` float NOT NULL DEFAULT 0,
  `Hb_EW` float NOT NULL DEFAULT 0,
  `Ha_EW` float NOT NULL DEFAULT 0,
  `Cloudy_version` varchar(20) NOT NULL DEFAULT 0,
  `bad` int(11) NOT NULL DEFAULT '0',
  `abion` tinyint(1) NOT NULL DEFAULT '0',
  `teion` tinyint(1) NOT NULL DEFAULT '0',
  `temis` tinyint(1) NOT NULL DEFAULT '0',
  `interpol` int(11) NOT NULL DEFAULT '0',
  `datetime` datetime NOT NULL DEFAULT 0,
  `N_pending` bigint(20) NOT NULL DEFAULT 0,
  `host` varchar(180) NOT NULL DEFAULT '',
  `N1` bigint(20) NOT NULL DEFAULT -1,
  `N2` bigint(20) NOT NULL DEFAULT -1,
  `W1` float NOT NULL DEFAULT 1,
  `Radio_2.5GHz` float NOT NULL DEFAULT 0,
  `Radio_4.9GHz` float NOT NULL DEFAULT 0,
  `Radio_12GHz` float NOT NULL DEFAULT 0,
  `Radio_20GHz` float NOT NULL DEFAULT 0,
"""


def init_lines(OVN_dic=OVN_dic, MdB=None, delete_before=False):
    table = OVN_dic['lines_table']
    
    if MdB is None:
        MdB = pc.MdB(OVN_dic = OVN_dic)
    
    if delete_before:
        command = 'DROP TABLE IF EXISTS {0};'.format(table)
        MdB.exec_dB(command)
    command = """CREATE TABLE IF NOT EXISTS {0} (
`Nl` bigint(20) NOT NULL AUTO_INCREMENT,
`label` varchar(15) DEFAULT NULL,
`id` varchar(20) DEFAULT NULL,
`lambda` double DEFAULT NULL,
`name` varchar(40) NOT NULL,
`used` int(2) DEFAULT 1,
PRIMARY KEY (`Nl`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1;
""".format(table)
    MdB.exec_dB(command)
    
    command = 'INSERT INTO {0} (`label`, `id`, `lambda`, `name`) VALUES '.format(table)
    for line in lines_list:
        command += "('{0[0]}', '{0[1]}', {0[2]}, '{0[3]}'), ".format(line)
    command = command[:-2]
    command += ';'
    MdB.exec_dB(command)
    MdB.close_dB()
    
def print_lines():
    """
    ('CL_3_335317A', 'Cl 3', 3353.17, 'Cl 3 3353.17A'),

    """
    for line in lines_list:

        ide = line[1]
        label = line[0]
        if label[-2:] != 'PN':
            lambda_ = line[2]
            if lambda_ > 1000:
                lambda_str = '{0:5.2f}'.format(lambda_)
            elif lambda_ > 100:
                lambda_str = '{0:5.3f}'.format(lambda_)
            elif lambda_ > 10:
                lambda_str = '{0:5.4f}'.format(lambda_)
            else:
                lambda_str = '{0:5.5f}'.format(lambda_)
            unit = label[-1]
            if unit == 'C':
                unit = 'M'
            C_str = '{0} {1}{2}'.format(ide, lambda_str, unit)
        print('{:15s} | {:15s} | {}'.format(label, C_str, line[3]))

        
    
def init_SEDs(OVN_dic=OVN_dic, MdB=None,delete_before=False):
    table = OVN_dic['seds_table']
    
    if MdB is None:
        MdB = pc.MdB(OVN_dic = OVN_dic)
    
    if delete_before:
        command = 'DROP TABLE IF EXISTS {0};'.format(table)
        MdB.exec_dB(command)
    command = """CREATE TABLE IF NOT EXISTS {0} (
`N` bigint(20) NOT NULL AUTO_INCREMENT,
`ref` varchar(40) NOT NULL DEFAULT '',
`sed_name` varchar(40) NOT NULL DEFAULT '',
`atm_cmd` varchar(60) NOT NULL DEFAULT '',
`atm_file` varchar(40) NOT NULL DEFAULT '',
`atm1` double DEFAULT NULL,
`atm2` double DEFAULT NULL,
`atm3` double DEFAULT NULL,
`lumi_unit` varchar(40) NOT NULL DEFAULT '',
`lumi` double DEFAULT NULL,
PRIMARY KEY (`N`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1;
""".format(table)
    MdB.exec_dB(command)
    
def init_pending(OVN_dic=OVN_dic, MdB=None,delete_before=False):
    
    table = OVN_dic['pending_table']
    
    if MdB is None:
        MdB = pc.MdB(OVN_dic = OVN_dic)
    
    if delete_before:
        command = 'DROP TABLE IF EXISTS {0};'.format(table)
        MdB.exec_dB(command)

    command = "CREATE TABLE IF NOT EXISTS {0} (".format(table)
    command += fields1
    for elem in elem_list:
        command += '`{0}` double NOT NULL DEFAULT -40,'.format(elem[0])
    command += """`priority` int(11) DEFAULT 10,
  `procID` bigint(20) DEFAULT -1,
  `lock` int(11) DEFAULT 0,
  PRIMARY KEY (`N`),
  KEY `status` (`status`),
  KEY `priority` (`priority`)
  ) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;
"""

    MdB.exec_dB(command)
    MdB.close_dB()
    
def init_tab(OVN_dic=OVN_dic, MdB=None,delete_before=False):
    table = OVN_dic['master_table']
    if MdB is None:
        MdB = pc.MdB(OVN_dic = OVN_dic)
    
    if delete_before:
        command = 'DROP TABLE IF EXISTS {0};'.format(table)
        MdB.exec_dB(command)
        
    command = "CREATE TABLE IF NOT EXISTS {0} (".format(table)
    command += fields1
    for elem in elem_list:
        command += '`{0}` double NOT NULL DEFAULT -40,'.format(elem[0])
    for line in lines_list:
        command += "`{0[0]}` double NOT NULL DEFAULT 0, ".format(line)
        command += "`{0[0]}_rad` double NOT NULL DEFAULT 0, ".format(line)
    command += fields2
    command += """PRIMARY KEY (`N`),
  KEY `ref` (`ref`),
  KEY `user` (`user`),
  KEY `atm_file` (`atm_file`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;
"""
    MdB.exec_dB(command)
    MdB.close_dB()
    
def init_teion(OVN_dic=OVN_dic, MdB=None, delete_before=False):
    table = OVN_dic['teion_table']
    
    if MdB is None:
        MdB = pc.MdB(OVN_dic = OVN_dic)
    
    if delete_before:
        command = 'DROP TABLE IF EXISTS {0};'.format(table)
        MdB.exec_dB(command)

    command = "CREATE TABLE IF NOT EXISTS {0} (`N` bigint(20) NOT NULL DEFAULT '0',".format(table)
    command += "`ref` varchar(40) NOT NULL ,"
    for elem in elem_list:
        for i in range(elem[1]+1):
            command += "`T_{0}_vol_{1}` double NOT NULL DEFAULT '-40',".format(elem[0], i)
            command += "`T_{0}_rad_{1}` double NOT NULL DEFAULT '-40',".format(elem[0], i)
    command += "PRIMARY KEY (`N`) ) ENGINE=MyISAM DEFAULT CHARSET=latin1;"
    MdB.exec_dB(command)
    MdB.close_dB()

def init_abion(OVN_dic=OVN_dic, MdB=None, delete_before=False):
    table = OVN_dic['abion_table']
    
    if MdB is None:
        MdB = pc.MdB(OVN_dic = OVN_dic)
    
    if delete_before:
        command = 'DROP TABLE IF EXISTS {0};'.format(table)
        MdB.exec_dB(command)

    command = "CREATE TABLE IF NOT EXISTS {0} (`N` bigint(20) NOT NULL DEFAULT '0',".format(table)
    command += "`ref` varchar(40) NOT NULL ,"

    for elem in elem_list:
        for i in range(elem[1]+1):
            command += "`A_{0}_vol_{1}` double NOT NULL DEFAULT '-40',".format(elem[0], i)
            command += "`A_{0}_rad_{1}` double NOT NULL DEFAULT '-40',".format(elem[0], i)
    command += "PRIMARY KEY (`N`) ) ENGINE=MyISAM DEFAULT CHARSET=latin1;"
    MdB.exec_dB(command)
    MdB.close_dB()

def init_temis(OVN_dic=OVN_dic, MdB=None, delete_before=False):
    table = OVN_dic['temis_table']
    
    if MdB is None:
        MdB = pc.MdB(OVN_dic = OVN_dic)
    
    if delete_before:
        command = 'DROP TABLE IF EXISTS {0};'.format(table)
        MdB.exec_dB(command)

    command = "CREATE TABLE IF NOT EXISTS {0} (`N` bigint(20) NOT NULL DEFAULT '0',".format(table)
    command += "`ref` varchar(40) NOT NULL ,"
    for line in lines_list:
        command += "`T_{0[0]}` double NOT NULL DEFAULT 0, ".format(line)
    command += "PRIMARY KEY (`N`) ) ENGINE=MyISAM DEFAULT CHARSET=latin1;"
    MdB.exec_dB(command)
    MdB.close_dB()
    
def init_procIDs(OVN_dic=OVN_dic, MdB=None, delete_before=False):
    table = OVN_dic['procIDs_table']
    
    if MdB is None:
        MdB = pc.MdB(OVN_dic = OVN_dic)
    
    if delete_before:
        command = 'DROP TABLE IF EXISTS {0};'.format(table)
        MdB.exec_dB(command)
    command = """CREATE TABLE IF NOT EXISTS {0} (
  `ID` bigint(20) NOT NULL AUTO_INCREMENT,
  `proc_name` varchar(80) NOT NULL,
  `datetime` datetime NOT NULL DEFAULT 0,
  `user`  varchar(80) NOT NULL,
  `host`  varchar(80) NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=3 ;
""".format(table)
    MdB.exec_dB(command)
    MdB.close_dB()

def update_lines(OVN_dic=OVN_dic, MdB=None):
    
    if MdB is None:
        MdB = pc.MdB(OVN_dic = OVN_dic)
    lines_tab =  MdB.get_fields(OVN_dic['master_table'])
    lines_temis = MdB.get_fields(OVN_dic['temis_table'])
    for line in lines_list:
        if line[0] not in lines_tab:
            command = 'ALTER TABLE {0} ADD `{1}` double NOT NULL DEFAULT 0;'.format(OVN_dic['master_table'], line[0])
            MdB.exec_dB(command)
            print('Adding line {0}'.format(line[0]))
        if line[0]+'_rad' not in lines_tab:
            command = 'ALTER TABLE {0} ADD `{1}_rad` double NOT NULL DEFAULT 0;'.format(OVN_dic['master_table'], line[0])
            MdB.exec_dB(command)
            print('Adding line {0}_rad'.format(line[0]))
        if 'T_{0}'.format(line[0]) not in lines_temis:
            command = 'ALTER TABLE {0} ADD `T_{1}` double NOT NULL DEFAULT 0;'.format(OVN_dic['temis_table'], line[0])
            MdB.exec_dB(command)
    lines_temis = MdB.get_fields(OVN_dic['temis_table'])
    for line in lines_temis:
        line_label = line[2:]
        if line_label not in [l[0] for l in lines_list]:
            print('Line to be removed: {0}'.format(line))
        

def init_all(delete_before=False):
    # desn't work if delete_before not set (or delete table from mysql before using it)
    # must define OVN_dic
    """
    From root@mysql:
        CREATE DATABASE 3MdB_17;
        GRANT ALL PRIVILEGES ON 3MdB_17.* TO 'OVN_admin'@'localhost';
    """
    init_lines(delete_before=delete_before)
    init_pending(delete_before=delete_before)
    init_tab(delete_before=delete_before)
    init_teion(delete_before=delete_before)
    init_abion(delete_before=delete_before)
    init_temis(delete_before=delete_before)
    init_SEDs(delete_before=delete_before)
    init_procIDs(delete_before=delete_before)
        