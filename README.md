_CS581: TEAM 2 - Ridesharing Project_
=======================================================
## Ankita Acharya, Sneha Dattatraya Shet, Amit Panthi, Yukthi Papanna Suresh 

### Requirements:
  - Python 3
  - New York Taxi Data 
   
  - To install additional required dependencies run the command:
  
        pip3 install -r requirements.txt
     
          
### Graphhopper API startup:
  1. Install the latest JRE and get GraphHopper Server as zip from <a href=https://graphhopper.com/public/releases/graphhopper-web-0.10.3-bin.zip>Graphhopper API</a>. Unzip it.
  2. Copy this OSM file into the SAME unzipped directory: <a href=https://download.geofabrik.de/north-america/us/new-york-latest.osm.pbf >new-york-latest.osm.pbf</a>
  3. Start GraphHopper Maps via: java -jar graphhopper-web-0.10.3-with-dep.jar jetty.resourcebase=webapp config=config-example.properties datareader.file=new-york-latest.osm.pbf. 
  4. Test to see if its running after you see 'Started server at HTTP 8989' by going to http://localhost:8989/ and you should see a map of New York.
  5. Keep this running when executing our program because this is the API
  
### Run Instructions:
  1. Download all the data files found in the instructions of Ride Sharing Graph.ipynb 
  2. The folder contains two main subfolders : Data folder and Distance Folder. Data ranges from Jan 2015 - Dec 2015
  3. **Note:** these precomputated distance files were created by running Distance Precomputation.ipynb. Additionally, only data for 2015 has been cleaned and precomputated in the available files
  3. Start the graphhopper server according to instructions above
  4. Three possible configurations are available to run this algorithm:
        A: one day data 
         B: specified minutes
         C: entire year 
    
  5. **Note:** To run configuration A or B, please follow the instructions defined by Ride Sharing Graph.ipynb
  6. For configuration C, run the notebook: 
     Run for year 2015.ipynb