#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PLANURB - Agencia Municipal de Meio Ambiente e Planejamento Urbano     Autor: Alberto T. Nagao     V 2.0
import io
import os
import arcpy
from math import cos, sin, radians 
arcpy.env.overwriteOutput = True	

def ptor2ptfin( ppx, ppy, angle, dist): 
    ''' position of the point located at a distance dist and azimuth angle from the point p ''' 
    dist_x, dist_y = (float(dist) * sin(radians(angle)), float(dist) * cos(radians(angle)))
    #arcpy.AddMessage("distx:{}: disty:{}:".format(dist_x, dist_y))
    xfinal = float(ppx) + dist_x
    yfinal = float(ppy) + dist_y
    return [xfinal,yfinal] 

def principal():
    global arquivo
    dicEPSG = {'Corrego Alegre - Meridiano Central 57 S':'22521'
    ,'Corrego Alegre - Meridiano Central 51 S':'22522'
    ,'Corrego Alegre - Meridiano Central 45 S':'22523'
    ,'Corrego Alegre - Meridiano Central 39 S':'22524'
    ,'Corrego Alegre - Meridiano Central 33 S':'22525'
    ,'SAD69 - Meridiano Central 75 N':'29168'
    ,'SAD69 - Meridiano Central 75 S':'29188'
    ,'SAD69 - Meridiano Central 69 N':'29169'
    ,'SAD69 - Meridiano Central 69 S':'29189'
    ,'SAD69 - Meridiano Central 63 N':'29170'
    ,'SAD69 - Meridiano Central 63 S':'29190'
    ,'SAD69 - Meridiano Central 57 S':'29191'
    ,'SAD69 - Meridiano Central 51 S':'29192'
    ,'SAD69 - Meridiano Central 45 S':'29193'
    ,'SAD69 - Meridiano Central 39 S':'29194'
    ,'SAD69 - Meridiano Central 33 S':'29195'
    ,'SIRGAS 2000 - Meridiano Central 75 N':'31972'
    ,'SIRGAS 2000 - Meridiano Central 75 S':'31978'
    ,'SIRGAS 2000 - Meridiano Central 69 N':'31973'
    ,'SIRGAS 2000 - Meridiano Central 69 S':'31979'
    ,'SIRGAS 2000 - Meridiano Central 63 N':'31974'
    ,'SIRGAS 2000 - Meridiano Central 63 S':'31980'
    ,'SIRGAS 2000 - Meridiano Central 57 S':'31981'
    ,'SIRGAS 2000 - Meridiano Central 51 S':'31982'
    ,'SIRGAS 2000 - Meridiano Central 45 S':'31983'
    ,'SIRGAS 2000 - Meridiano Central 39 S':'31984'
    ,'SIRGAS 2000 - Meridiano Central 33 S':'31985'
    ,'WGS 84  - Meridiano Central 75 N':'32618'
    ,'WGS 84  - Meridiano Central 75 S':'32718'
    ,'WGS 84 - Meridiano Central 69 N':'32619'
    ,'WGS 84 - Meridiano Central 69 S':'32719'
    ,'WGS 84 - Meridiano Central 63 N':'32620'
    ,'WGS 84 - Meridiano Central 63 S':'32720'
    ,'WGS 84 - Meridiano Central 57 S':'32721'
    ,'WGS 84 - Meridiano Central 51 S':'32722'
    ,'WGS 84 - Meridiano Central 45 S':'32723'}
    with io.open(arquivo, "r",encoding='latin-1')  as f:
        mem = f.readlines()		
        cont = 0
        for linha in mem:		
            if (linha.find('Inicia-se') != -1):
                #arcpy.AddMessage("'Inicia-se' esta na posicao {}".format(linha.find('Inicia-se')))		
                linB=linha[linha.find('Inicia-se'):linha.find('encerrando esta')+26]
                coordes =[]				
                while (linB.find('rtice P') != -1):
                    linA = linB
                    #Vert = linA[linA.find('rtice P')+6:linA.find(',',linA.find('rtice P')+6)]
                    y = float(linA[linA.find(', de coordenadas N')+19:linA.find(' m e E',linA.find(', de coordenadas N')+19)]) #.replace('.',','))
                    x = float(linA[linA.find('m e E')+6:linA.find(' m',linA.find('m e E')+6)]) #.replace('.',','))
                    # Validar o ponto senão abortar
                    coordes.append([x,y])
                    linB = linA[linA.find('m e E')+18:] 
                datumb = linha[linha.find('Datum ')+6:linha.find('com Meridiano Central ',linha.find('Datum ')+6) - 1]
                meridianob = linha[linha.find('Central ')+8:linha.find('Central ')+11]
                #para o Brasil verificar se latitude entre 6.262.800 e 10.000.000 entao hemisf='sul' senao entre 0 e 583.380 hemisf='norte'
                if float(y) > 6262800:  #.replace(',','.')
                    hemisf = "S"					
                elif float(y) < 583380: #.replace(',','.')
                    hemisf = "N"
                else:
                    arcpy.AddMessage("Nao foi possivel determinar o hemisferio desta Coordenada {}  {}".format(x, y))
                datum = datumb.strip() + " - Meridiano Central " + str(abs(int(meridianob)))+ " " + hemisf
                if datum not in dicEPSG:
                    arcpy.AddMessage("datum:{}: não encontrado na Tabela EPSG mais utilizados".format(datum))	
                    break
                #arcpy.AddMessage("ESPG:{}:".format(dicEPSG[datum]))
                sr = arcpy.SpatialReference(int(dicEPSG[datum]))
                pasta = os.path.dirname(arquivo)
                cont += 1
                nameshp = "Poligono" + str(cont) + ".shp"				
                arcpy.CreateFeatureclass_management(pasta, nameshp, "POLYGON", spatial_reference=sr)		
                polig = os.path.join(os.path.dirname(arquivo), nameshp)
                polygon = arcpy.Polygon(arcpy.Array([arcpy.Point(*a) for a in coordes]), sr)
                cursor = arcpy.da.InsertCursor(polig, ["SHAPE@"])
                cursor.insertRow([polygon]) 
                # Adiciona o "Poligono" no Data Frame
                mxd = arcpy.mapping.MapDocument("CURRENT")
                df = arcpy.mapping.ListDataFrames(mxd)[0]
                newlayer1 = arcpy.mapping.Layer(polig)
                arcpy.mapping.AddLayer(df, newlayer1, "TOP") 
				# Rename o "Polígono" pelo nome da pasta da variavel 'arquivo'
                layers = arcpy.mapping.ListLayers(mxd)
                for lyr in layers:
                    if lyr.name == "Poligono":
                        lyr.name = os.path.basename(os.path.dirname(arquivo))
            elif 'marco M-01' in linha:
                linb = linha[linha.find('marco M-01'):linha.find('fechando assim o') - 1]			
                if (linha.find('Sul e Longitude') == -1):					
                    hemisf = "N"
                else:
                    hemisf = "S"					
                datumb = linha[linha.find('Datum ')+6:linha.find(' e ',linha.find('Datum ')+6)].replace("-","")
                meridianob = linha[linha.find('central ')+8 : linha.find(' WGr',linha.find('central ')+8)-1]
                py = float(linha[linha.find('coordenada plana UTM N') + 23:linha.find('m e E ',linha.find('coordenada plana UTM N') + 23)].replace(".","").replace(",",".").strip())
                px = float(linha[linha.find('m e E') + 6:linha.find('m,',linha.find('m e E') + 6)].replace(".","").replace(",",".").strip())
                coordes =[]
                #arcpy.AddMessage("px:{}    py:{}::".format(str(px),str(py)))
                coordes.append([px,py])	
                while (linb.find('ncia de') != -1):
                    linA = linb
                    dista = linA[linA.find('ncia de') + 8:linA.find('m e', linA.find('ncia de') + 8)].replace(".","").replace(",",".").strip()
                    graus = linA[linA.find('azimute plano de') + 17:linA.find(' chega-se ao', linA.find('azimute plano de') + 17)].strip()
                    #arcpy.AddMessage("Graus:{}:".format(str(graus)))
                    lg = len(graus) - 7
                    azimu = float(graus[:lg]) + (float(graus[lg+1:lg+3])/60) + (float(graus[lg+4:lg+6])/360)
                    #arcpy.AddMessage('px:{}: py:{}:     Direcao:{}-{}-{}: distancia:{}: '.format(str(px), str(py), graus[:lg], graus[lg+1:lg+3], graus[lg+4:lg+6],dista))
                    pxy = ptor2ptfin(px, py, azimu, dista)
                    coordes.append(pxy)
                    #arcpy.AddMessage(pxy)
                    px, py = float(pxy[0]), float(pxy[1])
                    #arcpy.AddMessage("px:{}    py:{}::".format(str(px),str(py)))					
                    linb = linA[linA.find('chega-se ao marco')+24:]					
                datum = datumb.strip() + " - Meridiano Central " + str(abs(int(meridianob)))+ " " + hemisf
                if datum not in dicEPSG:
                    arcpy.AddMessage ("datum:{}: nao encontrado na Tabela EPSG mais utilizados".format(datum))
                #arcpy.AddMessage("ESPG:{}:".format(dicEPSG[datum]))	
                sr = arcpy.SpatialReference(int(dicEPSG[datum]))
                pasta = os.path.dirname(arquivo)
                cont += 1
                nameshp = "Poligono" + str(cont) + ".shp"				
                arcpy.CreateFeatureclass_management(pasta, nameshp, "POLYGON", spatial_reference=sr)		
                polig = os.path.join(os.path.dirname(arquivo), nameshp)
                polygon = arcpy.Polygon(arcpy.Array([arcpy.Point(*a) for a in coordes]), sr)
                cursor = arcpy.da.InsertCursor(polig, ["SHAPE@"])
                cursor.insertRow([polygon]) 
                # Adiciona o "Poligono" no Data Frame
                mxd = arcpy.mapping.MapDocument("CURRENT")
                df = arcpy.mapping.ListDataFrames(mxd)[0]
                newlayer1 = arcpy.mapping.Layer(polig)
                arcpy.mapping.AddLayer(df, newlayer1, "TOP") 
				# Rename o "Polígono" pelo nome da pasta da variavel 'arquivo'
                layers = arcpy.mapping.ListLayers(mxd)
                for lyr in layers:
                    if lyr.name == "Poligono":
                        lyr.name = os.path.basename(os.path.dirname(arquivo))
            elif linha.strip() == "":
                arcpy.AddMessage("Linha em branco")				
            else:
                arcpy.AddMessage("Este Memorial Descritivo nao tem formatacao Reconhecida")	

def todasPastas():
	global pasta, arquivo
	for (dirpath, dirs, files) in os.walk(pasta):
		for fname in files:
			if fname == '*.txt':
				arcpy.env.workspace = dirpath
				arquivo = os.path.join(dirpath,fname)
				principal()

if __name__ == '__main__':	
	arquivo = arcpy.GetParameterAsText(0)
	if arquivo:
		pasta = os.path.dirname(arquivo)
		arcpy.env.workspace = pasta
		principal()
	else:
		pasta = arcpy.GetParameterAsText(1)
		todasPastas()
	arcpy.RefreshActiveView()
	arcpy.RefreshTOC()
