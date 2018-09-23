#########################################################################
#
#      Title:       Plaxis 2d and Plaxis 3d Archiving Classes
#
#########################################################################
#
#      Description: Python classes to archive and delete Plaxis 2d and Plaxis 3d analysis models
#
#              
#               my_path = r'\\eu.aecomnet.com\euprojectvol\UKCRD1-TI\Projects\14\geotech1\GEO-3523'
#               my_module = imp.find_module('PlaxisArchive', [my_path])
#               PlaxisArxhive = imp.load_module('PlaxisArchive', *my_module)  
#
#               from PlaxisArchive import PlaxisArchive
#
#               pa = PlaxisArchive()
#
#               pa.setIncludeSubFolder(True)
#               pa.setOverWrite(True)
#               pa.setDeleteModel(True)
#               pa.setOnlyBeforeDate('2018-09-14')
#               pa.setSummaryFileOut(r'C:\Users\ThomsonSJ\Documents\Plaxis_files_2018-09-16.csv')
#               pa.setSummaryOnly(False)
#
#               pa.Archive (sfolder=r'C:\Users\ThomsonSJ\Documents')
#
#
#
#########################################################################
#
#########################################################################
#
#       Author      Thomson, Simon simon.thomson@aecom.com
#
##########################################################################
#
#       Version:    Beta 0.0.3
#
##########################################################################
#
#       Date:       2018 September 
#
###########################################################################


import os
import shutil
import zipfile
import stat
import datetime as dt
import time
import string

class PlaxisArchive (object):
    
    def __init__(self):
        
        global archiveExt
        global includesubfolder
        global overwrite
        global onlybeforedate
        global deletemodel
        global getsummaryonly
        global summaryfile
        global includezipfile
        
        self.includesubfolder = False
        self.overwrite = False
        self.onlybeforedate = None
        self.deletemodel = False
        self.summaryonly = False
        self.summaryfile = None
        self.includezipfile = False
        
        self.setPlaxisFileExtensions()
        
    def setDeleteModel(self, value):
        self.deletemodel = value
    def setOverWrite(self, value):
        self.overwrite = value
    def setSummaryFileOut(self, value):
        self.summaryfile = value
        header = "modelfile,ext,modify_time,access_time,size \n"
        with open(self.summaryfile, "w") as file:
            file.write (header)
            file.close     
        print (self.summaryfile + ' ready')
    def setSummaryOnly(self, value):
        self.summaryonly = value   
    def setIncludeSubFolder(self, value):
        self.includesubfolder = value
    def setOnlyBeforeDate (self, value):
        self.onlybeforedate = dt.datetime.strptime(value, '%Y-%m-%d')
    def setIncludeZipFile(self, value):
        self.includezipfile=value
    def setPlaxisFileExtensions(self):
        self.archiveExt = {'.p3dx':'.p3dxdat',
                            '.p3d':'.p3dat',
                            '.p2d':'.p2dat',
                            '.p2dx':'.p2dxdat'
                          }
       
    def Archive ( 
                self,
                deletemodel=None,
                overwrite=None,
                summaryfileout=None,
                summaryonly=None,
                includezipfile=None,
                includesubfolder=None,
                onlybeforedate=None,
                sfile=None,
                sfolder=None,
                ):
        
        if not deletemodel is None:
            self.setDeleteModel(deletemodel)
        if not overwrite is None:
            self.setOverWrite(overwrite)
        if not summaryfileout is None:
            self.setSummaryFileOut(summaryfileout)
        if not summaryonly is None:
            self.setSummaryOnly(summaryonly)
        if not includesubfolder is None:
            self.setIncludeSubFolder(includesubfolder)
        if not onlybeforedate is None:
            self.setOnlyBeforeDate(onlybeforedate)
        if not includezipfile is None:
            self.setIncludeZipFile(includezipfile)
            
        folders=[]
        files=[]
        
        if (sfile):
            if self.isModelZipFile(sfile):
                if self.includezipfile:
                    size = self.zip_summary(zipfile=sfile)
                    print ('found file:' + sfile + ' (' + '{0:.3f}'.format(size/1e9) + 'Gb)')
                    
            if self.isModelFile(sfile):
                if self.isForArchiving(sfile):
                    size = self.model_summary(modelfile=sfile)
                    print ('found file:' + sfile + ' (' + '{0:.3f}'.format(size/1e9) + 'Gb)')
                    if not self.summaryonly:
                        if self.model_pack(modelfile=sfile):
                            self.model_delete(modelfile=sfile)
                                
        if (sfolder):
            for (path, foldernames, filenames) in os.walk(sfolder):
                files.extend(filenames)
                folders.extend(foldernames)
                break
            for file in files:
                if self.isModelFile(file) or self.isModelZipFile(file):
                    self.Archive (sfile=path + '\\' + file)
    
        if (self.includesubfolder):
            for folder in folders:                         
                if not self.isModelFolder(folder):
                    print (' searching:' +  path + '\\' + folder)
                    self.Archive (sfolder = path + '\\' + folder)
    
    def model_pack (self,
                    modelfile,
                    ):
        try:
            
            file, ext =  os.path.splitext(modelfile)
            archive_name = self.getNextFileName(file + '_' + ext[1:],'.zip', len(file)) 
            if ext.lower() in self.archiveExt:
                modelfolder = file +  self.archiveExt.get(ext.lower(),"none")
                if os.path.isdir(modelfolder):
                    print ('and folder:' + modelfolder)
                    head,tail =  os.path.split(modelfolder)
                    shutil.make_archive (base_name=archive_name,
                                        format='zip',
                                        root_dir=head,
                                        base_dir=tail
                                        )
                    archive = zipfile.ZipFile(archive_name + '.zip', 'a')           
                    archive.write(modelfile,os.path.basename(modelfile))
                    archive.close()
                    print ('  archived:' + archive_name + '.zip')
                    return True
        except Exception as e:
            print (e)
            return False
        
                
    def model_delete (self,
                    modelfile,
                      ):
        try:
            file, ext =  os.path.splitext(modelfile) 
            if ext.lower() in self.archiveExt:
                modelfolder = file + self.archiveExt.get(ext.lower(),"none")
                if self.deletemodel:
                    if os.path.isfile(modelfile) and os.path.isdir(modelfolder):
                        os.remove(modelfile) 
                        print ('  del file:' + modelfile)
                        shutil.rmtree(modelfolder)
                        print ('and folder:' + modelfolder)
                        return True
            
        except Exception as e:
            print (e)
            return False

    def isModelFolder(self,
                      folder):
        for ex, fex in self.archiveExt.items():
            pos = -len(fex)
            exf = folder[pos:]
            if exf.lower() == fex:
                return True
        
        return False
    
    def isModelFile(self,
                      file):
        for ex in self.archiveExt:
            pos = -len(ex)
            exf = file[pos:]
            if exf.lower() == ex:
                return True
        
        return False
 
    def isModelZipFile(self,
                        file):
        file1, ext =  os.path.splitext(file)
        # print (file1, ext)
        if ext.lower() == '.zip':
            for ex in self.archiveExt:
                pos = -len(ex) + 1
                exf = file1[pos:]
                if exf.lower() == ex[1:]:
                    return True
        
        return False                    
        
    def model_summary(self, modelfile):
        
        try:
            file, ext =  os.path.splitext(modelfile)
            size = 0
            if ext.lower() in self.archiveExt: 
                modelfolder = file +  self.archiveExt.get(ext.lower(),"none")
                st_file = os.stat(modelfile)
                size_folder = self.get_folder_size(modelfolder)
                time_format = "%Y-%m-%d %I:%M:%S %p"
                modify_time = time.strftime(time_format,time.localtime(st_file[stat.ST_MTIME]))
                access_time = time.strftime(time_format,time.localtime(st_file[stat.ST_ATIME]))
                size = st_file[stat.ST_SIZE] + size_folder
                model_info = modelfile + ',' + ext + ',' + modify_time + ',' + access_time + ',' + '{0:.3f}'.format(size)           
                if self.summaryfile is not None:
                    with open(self.summaryfile, "a") as file:
                        file.write (model_info + '\n')
                        file.close()
            return size                    
        except Exception as e:
            print (e)
            return 0
    
    def zip_summary(self, zipfile):
        
        try:
            file, ext =  os.path.splitext(zipfile)
            size = 0
            if ext.lower() == '.zip':
                st_file = os.stat(zipfile)
                time_format = "%Y-%m-%d %I:%M:%S %p"
                modify_time = time.strftime(time_format,time.localtime(st_file[stat.ST_MTIME]))
                access_time = time.strftime(time_format,time.localtime(st_file[stat.ST_ATIME]))
                size = st_file[stat.ST_SIZE]
                zip_info = zipfile + ',' + ext + ',' + modify_time + ',' + access_time + ',' + '{0:.3f}'.format(size)           
                if self.summaryfile is not None:
                    with open(self.summaryfile, "a") as file:
                        file.write (zip_info + '\n')
                        file.close()
            return size
        except Exception as e:
            print (e)
            return 0
            
    def get_folder_size(self, start_path = '.'):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(start_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        return total_size
       
    def insert_string(self, s1, s2, pos):
        
        s3 = s1[:pos]
        s3 += s2
        s3 += s1[pos:]
        
        return s3
        
    def getNextFileName (self, filename, ext, pos = None):
        
        if pos is None:
            pos = len(filename)
            
        retname = filename
        uniquename = filename + ext
        counter = 0
        
        if not self.overwrite:
            while os.path.isfile(uniquename):
                counter += 1
                retname = self.insert_string(filename, str(counter),pos)
                uniquename =  retname + ext
        return retname
        
    def isForArchiving(self, file):
        if os.path.isfile(file):
            if self.onlybeforedate:
                st = os.stat(file)    
                mtime = dt.datetime.fromtimestamp(st.st_mtime)
                if mtime > self.onlybeforedate:
                    return False
            return True
        else:
            return False

 
    def get_info(self, file_name):
        
        time_format = "%m/%d/%Y %I:%M:%S %p"
        file_stats = os.stat(file_name)
        modification_time = time.strftime(time_format,file_stats[stat.ST_MTIME])
        access_time = time.strftime(time_format,file_stats[stat.ST_ATIME])
        return modification_time, access_time

