# مرجع معادلات Excel الأصلية

هذا الملف يحتوي على جميع المعادلات المستخرجة من Excel للرجوع إليها.

---

## المتغيرات المسماة (Named Ranges)

```
W_O = العرض الكلي (meters)
W_C = العرض (عدد الألواح الكاملة)
W_F = كسر العرض (0 أو 0.5)

L1_O, L2_O, L3_O, L4_O = أطوال الأقسام
L1_C, L2_C, L3_C, L4_C = عدد الألواح لكل قسم
L1_F, L2_F, L3_F, L4_F = كسور الأطوال

L_O = الطول الكلي
L_O_C = مجموع ألواح الطول
L_O_F = مجموع كسور الطول

H_O = الارتفاع الكلي
H_C = الارتفاع (عدد الألواح)
H_F = كسر الارتفاع

N_PA = عدد الحواجز (Partitions)
```

---

## Sheet 10/9: Panel Formulas

### Manhole
```excel
=1+N_PA
```

### Roof Full (RF)
```excel
=IF(W_C*(L1_C+L2_C+L3_C+L4_C)-X6-X10-X11<0,0,W_C*(L1_C+L2_C+L3_C+L4_C)-X6-X10-X11)
```
حيث: X6=manhole, X10=?, X11=?

### Roof Half (RH)
```excel
=W_C*(L1_F+L2_F+L3_F+L4_F)+W_F*(L1_C+L2_C+L3_C+L4_C)
```

### Roof Quarter (RQ)
```excel
=IF(AND(W_F=1,OR(L1_F,L2_F,L3_F,L4_F)),L1_F+L2_F+L3_F+L4_F,0)
```
**ملاحظة مهمة**: W_F=1 يعني W_F يساوي 1 بالضبط (أي 0.5m panel)

### Panel Code Lookup
```excel
=HLOOKUP(H_O,$O$5:$W$115,Z6,FALSE)
```

### Sealing Tape (AB column)
```excel
=AA6*J6
```
حيث AA = tape per panel, J = quantity

---

## Sheet 12: Steel_Skid Formulas

### WFF-1990 (Main-L 2m)
```excel
=((IF(L_O_F>0,QUOTIENT(L_O-1.5,2),L_O_C/2)))*(W_C+W_F+1)*IF(BASIC_TOOL!D23=5,0,1)
```

### WFF-0990 (Main-L 1m)
```excel
=((IF(L1_F>0,MOD(L1_O-1.5,2),MOD(L1_C,2))+IF(L2_F>0,MOD(L2_O-1.5,2),MOD(L2_C,2))+IF(L3_F>0,MOD(L3_O-1.5,2),MOD(L3_C,2))+IF(L4_F>0,MOD(L4_O-1.5,2),MOD(L4_C,2)))*(W_C+W_F+1))*IF(BASIC_TOOL!D23=5,0,1)
```

### Main Beam Connector
```excel
=(W_C+W_F+1)*2*IF(BASIC_TOOL!D23=5,0,1)
```

### Cross Beam
```excel
=((SUM(M14:M27)/2)-1)*2*IF(BASIC_TOOL!D23=5,0,1)
```

### Width Frame (with ISEVEN)
```excel
=(IF(OR(W_O=3.5),1,0)+IF(W_O>3.5,IF(W_F=0,IF(ISEVEN(W_O),2,0),0))+IF(W_O>3.5,IF(W_F=1,IF(ISEVEN(W_O-1.5),2,0),0)))*IF(BASIC_TOOL!D23=5,0,1)
```

### Width Frame (with ISODD)
```excel
=(IF(W_O=3,2,IF(W_O=3.5,1,0))+IF(W_F=0,IF(W_O>3.5,IF(ISODD(W_O),2,0),0),0)+IF(W_F=1,IF(W_O>3.5,IF(ISODD(W_O-1.5),2,0),0),0))*IF(BASIC_TOOL!D23=5,0,1)
```

### Center Channel Bars
```excel
=(IF(W_F=0,IF(W_O>3.5,IF(ISEVEN(W_O),(W_O-4)/2*2,(W_O-3)/2*2),0),0)+IF(W_F=1,IF(W_O>4,IF(ISEVEN(W_O-1.5),(W_O-1.5-4)/2*2,(W_O-1.5-3)/2*2),0),0))*IF(BASIC_TOOL!D23=5,0,1)
```

### Sub-frames
```excel
=(IF(W_O>=3.5,(ROUND(W_O,0)-3),0)*(CEILING(L1_O,1)+CEILING(L2_O,1)+CEILING(L3_O,1)+CEILING(L4_O,1)-1))*IF(BASIC_TOOL!D23=5,0,1)
```

### Liner
```excel
=(ROUNDUP((W_C+W_F+1)*(CEILING(L1_O,1)+CEILING(L2_O,1)+CEILING(L3_O,1)+CEILING(L4_O,1)+1)*4.6,0))*IF(BASIC_TOOL!D23=5,0,1)
```
**Factor = 4.6 ثابت!**

---

## Sheet 13: BoltnNuts Formulas

### Panel-to-Panel Bolts
```excel
=(4*W_C+2*W_F)*(L1_C+L2_C+L3_C+L4_C+L1_F+L2_F+L3_F+L4_F-N_PA-1)
```

### Length-wise Joint Bolts
```excel
=(4*(L1_C+L2_C+L3_C+L4_C)+2*(L1_F+L2_F+L3_F+L4_F))*CEILING(W_O-1,1)
```

### Height-based Corner Bolts
```excel
=IF(H_O=2.5,1*4,0)+IF(H_O=3,1*4,0)+IF(H_O=3.5,2*4,0)+IF(H_O=4,2*4,0)+IF(H_O=4.5,3*4,0)+IF(H_O=5,3*4,0)
```

### Vertical Joint Bolts
```excel
=H_O*8*2*4
```

### Perimeter Bolts
```excel
=(L1_C+L2_C+L3_C+L4_C+W_C)*4*2+(L1_F+L2_F+L3_F+L4_F+W_F)*2*2
```

### Steel Skid Bolts
```excel
=2*Steel_Skid!$M$9+IF(OR(H_O>2.5,BASIC_TOOL!D17=2,BASIC_TOOL!D17=3),2*Steel_Skid!$M$9,0)
```

### Spare Factor
```excel
=ROUNDUP(AQ5*$AR$2,0)
```
حيث AR$2 = spare factor (e.g., 1.05)

---

## Sheet 17: Internal_Tie_rod1 Formulas

### Height Multiplier Lookup
```excel
=LOOKUP(H_O,AG11:AG19,AH11:AH19)
```
**يجب استخراج جدول AG11:AH19**

### Main Tie Rod Quantity
```excel
=LOOKUP(H_O,AG11:AG19,AH11:AH19)*((L1_C+L1_F-1)+IF(L2_O>1,(L2_C+L2_F-1),0)+IF(L3_O>1,(L3_C+L3_F-1),0)+IF(L4_O>1,(L4_C+L4_F-1),0))+IF(H_O>2,(H_F+H_C-2)*N_PA,0)
```

### Tie Rod Length (mm)
```excel
=(W_O)*1000-120
=(L1_O)*1000-120
=(L2_O)*1000-120
```

### Width Tie Rods
```excel
=LOOKUP(H_O,AG11:AG19,AH11:AH19)*(W_C+W_F-1)
```

### Tie Rod Code
```excel
=IF(BASIC_TOOL!$E$23=2,"TR-12M0280SA2","TR-12M0280SA4")
```

### Tie Rod VLOOKUP (جدول كبير)
```excel
=IFERROR(VLOOKUP(W_O,$AG$24:$BF$123,COLUMN(AH24)-COLUMN($AG$24)+1,0),0)
=IFERROR(VLOOKUP(L1_O,$AG$24:$BF$123,COLUMN(AH24)-COLUMN($AG$24)+1,0),0)
```
**جدول 100 صف × 26 عمود - يجب استخراجه**

---

## Sheet 14: External_Reinforcing Formulas

### Perimeter Count
```excel
=W_C+W_F-1+L_O_C+L_O_F-1-N_PA
```

### Height-based Angles (4.5-5m)
```excel
=IF(OR(H_O=4.5,H_O=5),(W_F+L1_F+L2_F+L3_F+L4_F)*2,0)
```

### Progressive Reinforcing
```excel
=IF(H_O>1,(W_F+L1_F+L2_F+L3_F+L4_F)*2,0)+IF(H_O>3.3,(W_F+L1_F+L2_F+L3_F+L4_F)*2,0)
```

### Tiered Reinforcing
```excel
=IF(OR(H_O=1.5,H_O=2),(W_F+L1_F+...)*2,0)+IF(OR(H_O=2.5,H_O=3),...*2*2,0)+IF(OR(H_O=3.5,H_O=4),...*2*3)+IF(OR(H_O=4.5,H_O=5),...*2*4)
```

### Corner Brackets
```excel
=IF(OR(H_O=3.5,H_O=3),4*2,0)+IF(OR(H_O=4,H_O=4.5),4*2*2,0)+IF(OR(H_O=5),4*3*2,0)
```

---

## Sheet 15: Internal_Reinforcing Formulas

### Base Perimeter
```excel
=(W_C+W_F-1+L_O_C+L_O_F-1-N_PA)*2
```

### WFB-1200 (Reinforcing Angle)
```excel
=(W_C+W_F-1+L_O_C+L_O_F-1-N_PA)*2
```

### WFB-0880 (Partition Angle)
```excel
=IF(OR(BASIC_TOOL!E15=0),IF(OR(H_O=1.5,H_O=2,H_O=2.5,H_O=3,H_O=3.5,H_O=4,H_O=4.5,H_O=5),(W_C+W_F-1)*N_PA,0),IF(OR(H_O=1.5),(W_C+W_F-1)*N_PA,0))
```

### WFB-0950 (Partition Plate) - Height Tiered
```excel
=IF(BASIC_TOOL!E15=0,IF(OR(H_O=3.5,H_O=4),(W_C+W_F-1)*N_PA,0)+IF(OR(H_O=4.5,H_O=5),(W_C+W_F-1)*2*N_PA,0), IF(OR(H_O=3,H_O=3.5),(W_C+W_F-1)*N_PA,0)+IF(OR(H_O=4,H_O=4.5),(W_C+W_F-1)*2*N_PA,0))
```

### Cross Plate X12 (معقدة)
```excel
=((IF(OR(H_O=2.5,H_O=3),W_C,0)+IF(OR(H_O=3.5,H_O=4),W_C*2,0)+IF(OR(H_O=4.5,H_O=5),W_C*3,0))*N_PA+IF(AND(BASIC_TOOL!E15=1,OR(H_O=2,H_O=2.5,H_O=3,H_O=3.5,H_O=4,H_O=4.5,H_O=5)),W_C,0))*N_PA
```

### Height > 4 Formula
```excel
=IF(H_O>4,(W_C)*(H_C+H_F-3),0)*N_PA
```

---

## Sheet 19: ETC Formulas

### Air Vent Code
```excel
=IF(BASIC_TOOL!H11<100,"WAV-0050A","WAV-0100A")
```

### Air Vent Quantity
```excel
=CEILING(W_C*L1_C/30,1)+CEILING(W_C*L2_C/30,1)+CEILING(W_C*L3_C/30,1)+CEILING(W_C*L4_C/30,1)
```

### Roof Supporter Code
```excel
="WRS-"&H_O*1000&"F"
```

### Internal Ladder Code
```excel
="WLD-"&H_O*1000&"FI"
```

### Internal Ladder Quantity
```excel
=N_PA+1
```

### External Ladder Code
```excel
="WLD-"&H_O*1000&"ZO"
```

### Silicon
```excel
=ROUNDUP(0.1*(W_C+W_F)*(L_O_C+L_O_F),0)
```

### Level Indicator
```excel
=IF(BASIC_TOOL!B27=1,"WLV-"&H_O*1000&"SET(G)",IF(BASIC_TOOL!B27=2,"WLV-0000SET(S)",""))
```

### Sealing Tape 50mm (يعتمد على أوراق أخرى!)
```excel
=Panel2!AB5+Internal_Reinforcing!AB25
```

### Sealing Tape 120mm
```excel
=4*H_O+1
```

### Additional Tape Calculations
```excel
=(W_O*(L1_C+L1_F+L2_C+L2_F+L3_C+L3_F+L4_C+L4_F+1)+L_O*(W_C+W_F+1))
=H_O*(W_C+W_F+1)*(2+N_PA)
=H_O*(L1_C+L2_C+L3_C+L4_C+L1_F+L2_F+L3_F+L4_F+1)*2
```

---

## جداول Lookup المطلوب استخراجها

### 1. Height Multiplier (sheet17: AG11:AH19)
```
H_O | Multiplier
----|----------
1.5 | ?
2.0 | ?
2.5 | ?
3.0 | ?
3.5 | ?
4.0 | ?
4.5 | ?
5.0 | ?
```

### 2. Tie Rod Length Table (sheet17: AG24:BF123)
جدول كبير يحتاج استخراج منفصل

### 3. Panel Code Table (sheet10: O5:W115)
جدول أكواد الألواح حسب الارتفاع

---

## ملاحظات مهمة

1. **BASIC_TOOL!D23=5** يعني "Except SKB" - لا steel skid
2. **BASIC_TOOL!E15** يتعلق بنوع العزل (Insulation)
3. **BASIC_TOOL!B27** يتعلق بنوع مؤشر المستوى (Level Indicator)
4. **BASIC_TOOL!H11** هي سعة الخزان (capacity)
5. جميع الارتفاعات تُعامل كحالات منفصلة في Excel (1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5)
