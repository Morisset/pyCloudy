import pyCloudy as pc


OVN_dic = {'host' : 'localhost',
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

lines_list = [('BAC___3646A', 'Bac ', 3646.0, 'BalmHead'), 
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
def init_lines(OVN_dic=OVN_dic, MdB=None,delete_before=False):
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
    command += """`DepthFrac` double NOT NULL DEFAULT 1,
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
  `logPhi` float NOT NULL DEFAULT 0,
  `logPhi0` float NOT NULL DEFAULT 0,
  `logPhi1` float NOT NULL DEFAULT 0,
  `logPhi2` float NOT NULL DEFAULT 0,
  `logPhi3` float NOT NULL DEFAULT 0,
  `logU_in` float NOT NULL DEFAULT '0',
  `logU_out` float NOT NULL DEFAULT '0',
  `logU_mean` float NOT NULL DEFAULT 0,
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
  `N1` bigint(20) NOT NULL DEFAULT -1,
  `N2` bigint(20) NOT NULL DEFAULT -1,
  `W1` float NOT NULL DEFAULT 1,
  PRIMARY KEY (`N`),
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
    command += "`ref` varchar(40) NOT NULL ,".format(elem[0], i)
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
    command += "`ref` varchar(40) NOT NULL ,".format(elem[0], i)

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
    command += "`ref` varchar(40) NOT NULL ,".format(elem[0], i)
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
        

def init_all():
    # desn't work if delete_before not set (or delete table from mysql before using it)
    # must define OVN_dic
    init_lines()
    init_pending()
    init_tab()
    init_teion()
    init_abion()
    init_temis()
    init_procIDs()
    init_SEDs()