EESchema Schematic File Version 4
EELAYER 29 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 2 8
Title ""
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L Device:Q_PMOS_GSD Q?
U 1 1 5D0FC85E
P 5950 1800
AR Path="/5D0E8934/5D0FC85E" Ref="Q?"  Part="1" 
AR Path="/5D18BE3E/5D0FC85E" Ref="Q?"  Part="1" 
AR Path="/5D18C93A/5D0FC85E" Ref="Q?"  Part="1" 
AR Path="/5D18D41E/5D0FC85E" Ref="Q?"  Part="1" 
AR Path="/5D18DF58/5D0FC85E" Ref="Q?"  Part="1" 
AR Path="/5D18EA36/5D0FC85E" Ref="Q?"  Part="1" 
F 0 "Q?" V 6293 1800 50  0000 C CNN
F 1 "FDN340P" V 6202 1800 50  0000 C CNN
F 2 "Package_TO_SOT_SMD:SOT-23" H 6150 1900 50  0001 C CNN
F 3 "https://www.onsemi.com/pub/Collateral/FDN340P-D.PDF" H 5950 1800 50  0001 C CNN
	1    5950 1800
	0    1    -1   0   
$EndComp
$Comp
L Transistor_BJT:MMBT3904 Q?
U 1 1 5D0FEF29
P 5450 3200
AR Path="/5D0E8934/5D0FEF29" Ref="Q?"  Part="1" 
AR Path="/5D18BE3E/5D0FEF29" Ref="Q?"  Part="1" 
AR Path="/5D18C93A/5D0FEF29" Ref="Q?"  Part="1" 
AR Path="/5D18D41E/5D0FEF29" Ref="Q?"  Part="1" 
AR Path="/5D18DF58/5D0FEF29" Ref="Q?"  Part="1" 
AR Path="/5D18EA36/5D0FEF29" Ref="Q?"  Part="1" 
F 0 "Q?" H 5641 3246 50  0000 L CNN
F 1 "MMBT3904" H 5641 3155 50  0000 L CNN
F 2 "Package_TO_SOT_SMD:SOT-23" H 5650 3125 50  0001 L CIN
F 3 "https://www.fairchildsemi.com/datasheets/2N/2N3904.pdf" H 5450 3200 50  0001 L CNN
	1    5450 3200
	1    0    0    -1  
$EndComp
$Comp
L Diode:BAT54W D?
U 1 1 5D0FFC85
P 7050 1850
AR Path="/5D0E8934/5D0FFC85" Ref="D?"  Part="1" 
AR Path="/5D18BE3E/5D0FFC85" Ref="D?"  Part="1" 
AR Path="/5D18C93A/5D0FFC85" Ref="D?"  Part="1" 
AR Path="/5D18D41E/5D0FFC85" Ref="D?"  Part="1" 
AR Path="/5D18DF58/5D0FFC85" Ref="D?"  Part="1" 
AR Path="/5D18EA36/5D0FFC85" Ref="D?"  Part="1" 
F 0 "D?" V 7004 1979 50  0000 L CNN
F 1 "BAT54W" V 7095 1979 50  0000 L CNN
F 2 "Package_TO_SOT_SMD:SOT-323_SC-70" H 7050 1675 50  0001 C CNN
F 3 "https://assets.nexperia.com/documents/data-sheet/BAT54W_SER.pdf" H 7050 1850 50  0001 C CNN
	1    7050 1850
	0    1    1    0   
$EndComp
$Comp
L Connector:Screw_Terminal_01x02 J?
U 1 1 5D100AC5
P 8050 1700
AR Path="/5D0E8934/5D100AC5" Ref="J?"  Part="1" 
AR Path="/5D18BE3E/5D100AC5" Ref="J?"  Part="1" 
AR Path="/5D18C93A/5D100AC5" Ref="J?"  Part="1" 
AR Path="/5D18D41E/5D100AC5" Ref="J?"  Part="1" 
AR Path="/5D18DF58/5D100AC5" Ref="J?"  Part="1" 
AR Path="/5D18EA36/5D100AC5" Ref="J?"  Part="1" 
F 0 "J?" H 8130 1692 50  0000 L CNN
F 1 "Screw_Terminal_01x02" H 8130 1601 50  0000 L CNN
F 2 "" H 8050 1700 50  0001 C CNN
F 3 "~" H 8050 1700 50  0001 C CNN
	1    8050 1700
	1    0    0    -1  
$EndComp
Wire Wire Line
	6150 1700 7050 1700
Wire Wire Line
	7050 1700 7850 1700
Connection ~ 7050 1700
$Comp
L power:GND #PWR0110
U 1 1 5D1075E1
P 7750 2000
AR Path="/5D0E8934/5D1075E1" Ref="#PWR0110"  Part="1" 
AR Path="/5D18BE3E/5D1075E1" Ref="#PWR?"  Part="1" 
AR Path="/5D18C93A/5D1075E1" Ref="#PWR?"  Part="1" 
AR Path="/5D18D41E/5D1075E1" Ref="#PWR?"  Part="1" 
AR Path="/5D18DF58/5D1075E1" Ref="#PWR?"  Part="1" 
AR Path="/5D18EA36/5D1075E1" Ref="#PWR?"  Part="1" 
F 0 "#PWR0110" H 7750 1750 50  0001 C CNN
F 1 "GND" H 7755 1827 50  0000 C CNN
F 2 "" H 7750 2000 50  0001 C CNN
F 3 "" H 7750 2000 50  0001 C CNN
	1    7750 2000
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR0111
U 1 1 5D107F93
P 7050 2000
AR Path="/5D0E8934/5D107F93" Ref="#PWR0111"  Part="1" 
AR Path="/5D18BE3E/5D107F93" Ref="#PWR?"  Part="1" 
AR Path="/5D18C93A/5D107F93" Ref="#PWR?"  Part="1" 
AR Path="/5D18D41E/5D107F93" Ref="#PWR?"  Part="1" 
AR Path="/5D18DF58/5D107F93" Ref="#PWR?"  Part="1" 
AR Path="/5D18EA36/5D107F93" Ref="#PWR?"  Part="1" 
F 0 "#PWR0111" H 7050 1750 50  0001 C CNN
F 1 "GND" H 7055 1827 50  0000 C CNN
F 2 "" H 7050 2000 50  0001 C CNN
F 3 "" H 7050 2000 50  0001 C CNN
	1    7050 2000
	1    0    0    -1  
$EndComp
Wire Wire Line
	7750 2000 7750 1800
Wire Wire Line
	7750 1800 7850 1800
$Comp
L power:GND #PWR0112
U 1 1 5D1083AF
P 5550 3400
AR Path="/5D0E8934/5D1083AF" Ref="#PWR0112"  Part="1" 
AR Path="/5D18BE3E/5D1083AF" Ref="#PWR?"  Part="1" 
AR Path="/5D18C93A/5D1083AF" Ref="#PWR?"  Part="1" 
AR Path="/5D18D41E/5D1083AF" Ref="#PWR?"  Part="1" 
AR Path="/5D18DF58/5D1083AF" Ref="#PWR?"  Part="1" 
AR Path="/5D18EA36/5D1083AF" Ref="#PWR?"  Part="1" 
F 0 "#PWR0112" H 5550 3150 50  0001 C CNN
F 1 "GND" H 5555 3227 50  0000 C CNN
F 2 "" H 5550 3400 50  0001 C CNN
F 3 "" H 5550 3400 50  0001 C CNN
	1    5550 3400
	1    0    0    -1  
$EndComp
$Comp
L Device:R_Small_US R?
U 1 1 5D1088C5
P 5550 2050
AR Path="/5D0E8934/5D1088C5" Ref="R?"  Part="1" 
AR Path="/5D18BE3E/5D1088C5" Ref="R?"  Part="1" 
AR Path="/5D18C93A/5D1088C5" Ref="R?"  Part="1" 
AR Path="/5D18D41E/5D1088C5" Ref="R?"  Part="1" 
AR Path="/5D18DF58/5D1088C5" Ref="R?"  Part="1" 
AR Path="/5D18EA36/5D1088C5" Ref="R?"  Part="1" 
F 0 "R?" H 5618 2096 50  0000 L CNN
F 1 "4.7k" H 5618 2005 50  0000 L CNN
F 2 "" H 5550 2050 50  0001 C CNN
F 3 "~" H 5550 2050 50  0001 C CNN
	1    5550 2050
	1    0    0    -1  
$EndComp
$Comp
L Device:R_Small_US R?
U 1 1 5D108D44
P 4950 3200
AR Path="/5D0E8934/5D108D44" Ref="R?"  Part="1" 
AR Path="/5D18BE3E/5D108D44" Ref="R?"  Part="1" 
AR Path="/5D18C93A/5D108D44" Ref="R?"  Part="1" 
AR Path="/5D18D41E/5D108D44" Ref="R?"  Part="1" 
AR Path="/5D18DF58/5D108D44" Ref="R?"  Part="1" 
AR Path="/5D18EA36/5D108D44" Ref="R?"  Part="1" 
F 0 "R?" V 4745 3200 50  0000 C CNN
F 1 "4.7k" V 4836 3200 50  0000 C CNN
F 2 "" H 4950 3200 50  0001 C CNN
F 3 "~" H 4950 3200 50  0001 C CNN
	1    4950 3200
	0    1    1    0   
$EndComp
$Comp
L power:+12V #PWR0113
U 1 1 5D109B67
P 4950 1700
AR Path="/5D0E8934/5D109B67" Ref="#PWR0113"  Part="1" 
AR Path="/5D18BE3E/5D109B67" Ref="#PWR?"  Part="1" 
AR Path="/5D18C93A/5D109B67" Ref="#PWR?"  Part="1" 
AR Path="/5D18D41E/5D109B67" Ref="#PWR?"  Part="1" 
AR Path="/5D18DF58/5D109B67" Ref="#PWR?"  Part="1" 
AR Path="/5D18EA36/5D109B67" Ref="#PWR?"  Part="1" 
F 0 "#PWR0113" H 4950 1550 50  0001 C CNN
F 1 "+12V" H 4965 1873 50  0000 C CNN
F 2 "" H 4950 1700 50  0001 C CNN
F 3 "" H 4950 1700 50  0001 C CNN
	1    4950 1700
	1    0    0    -1  
$EndComp
Wire Wire Line
	5750 1700 5550 1700
Wire Wire Line
	5950 2350 5550 2350
Wire Wire Line
	5550 2700 5550 3000
Wire Wire Line
	5550 2150 5550 2350
Wire Wire Line
	5550 1950 5550 1700
Connection ~ 5550 1700
Wire Wire Line
	5550 1700 4950 1700
Wire Wire Line
	5950 2000 5950 2350
Wire Wire Line
	5050 3200 5250 3200
Text HLabel 4450 3200 0    50   Input ~ 0
Enable
Wire Wire Line
	4450 3200 4850 3200
$Comp
L Device:R_Small_US R?
U 1 1 5D1A2245
P 5550 2600
AR Path="/5D0E8934/5D1A2245" Ref="R?"  Part="1" 
AR Path="/5D18BE3E/5D1A2245" Ref="R?"  Part="1" 
AR Path="/5D18C93A/5D1A2245" Ref="R?"  Part="1" 
AR Path="/5D18D41E/5D1A2245" Ref="R?"  Part="1" 
AR Path="/5D18DF58/5D1A2245" Ref="R?"  Part="1" 
AR Path="/5D18EA36/5D1A2245" Ref="R?"  Part="1" 
F 0 "R?" H 5618 2646 50  0000 L CNN
F 1 "4.7k" H 5618 2555 50  0000 L CNN
F 2 "" H 5550 2600 50  0001 C CNN
F 3 "~" H 5550 2600 50  0001 C CNN
	1    5550 2600
	1    0    0    -1  
$EndComp
Wire Wire Line
	5550 2350 5550 2500
Connection ~ 5550 2350
$EndSCHEMATC
