#encoding=utf-8
import GpxGeneTools as ggt

tool =  ggt.GpxGeneTools()
#tool.geneByUser()
tool.geneByUserDay()
print str(sum(tool.countDays)) +' available traces in total'