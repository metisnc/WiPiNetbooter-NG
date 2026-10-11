import csv, operator, subprocess, os, sys

def append_list_as_row(file_name, list_of_elem):
    with open(file_name, 'a+', newline='') as write_obj:
        csv_writer = csv.writer(write_obj)
        csv_writer.writerow(list_of_elem)

if os.path.exists('/boot/roms/n1-doom-1.0alpha1.bin.gz') == False:
    filename = '/var/www/html/csv/romsinfo.csv'
    columns = ['system','romname','image','video','description','lcd_description','manufacturer','year','genre','rating','orientation','controls','enabled','favourite','openjvs','openffb','game_id','audit_name']
    row_contents = ['Sega Naomi','n1-doom-1.0alpha1.bin.gz','doom.png','doom.mp4','Doom (Shareware)','Doom','ID',1993,'Action','AAMA - Red (Animated Violence Strong)','Horizontal','Digital (Stick)','Yes','No','generic','none','BDM0','n1-doom-1.0alpha1.bin.gz']
    append_list_as_row(filename, row_contents)
    data = csv.reader(open(filename),delimiter=',')
    header = next(data)
    data = sorted(data, key=operator.itemgetter(4))
    with open(filename, 'w', newline='') as write_obj:
        csv_writer = csv.writer(write_obj)
        csv_writer.writerow(columns)
        csv_writer.writerows(data)