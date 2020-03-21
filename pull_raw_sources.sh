#!/bin/sh
mkdir -p raw
cd raw
wget https://www.e-unwto.org/doi/suppl/10.5555/unwtotfb0702250119952018202001/suppl_file/0702250119952018202001.xlsx -O sg_outbound_travel.xlsx
wget https://www.e-unwto.org/doi/suppl/10.5555/unwtotfb0158250119952018202001/suppl_file/0158250119952018202001.xlsx -O tw_outbound_travel.xlsx
wget https://www.stb.gov.sg/content/dam/stb/documents/statistics-marketing-insights/international-visitor-arrivals/excel/Time%20Series%20-%20International%20Visitor%20Arrival%20Statistics_Jan2020.xlsx -O sg_inbound_travel.xlsx
# doesn't work
#wget https://admin.taiwan.net.tw/Handlers/FileHandler.ashx?fid=00f3147f-5961-4fe0-901d-c4fadf253ade&type=4&no=1 -O tw_inbound_travel.xlsx
cd ..
