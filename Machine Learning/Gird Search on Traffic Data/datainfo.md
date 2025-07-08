The following features are included in this dataset:

* ID This is a unique identifier of the accident record.
* Severity Shows the severity of the accident, a number between 1 and 3, where 1 indicates the least impact on traffic (i.e., short delay as a result of the accident) and 3 indicates a significant impact on traffic (i.e., long delay).	
* Start_Lat Shows latitude in GPS coordinate of the start point.	
* Start_Lng Shows longitude in GPS coordinate of the start point.	
* Distance(mi) The length of the road extent affected by the accident.
* Description Shows natural language description of the accident.
* Side Shows the relative side of the street (Right/Left) in address field.
* City Shows the city in address field.
* County Shows the county in address field.
* State	Shows the state in address field.
* Zipcode Shows the zipcode in address field.
* Country Shows the country in address field.
* Temperature(F) Shows the temperature (in Fahrenheit).
* Wind_Chill(F) Shows the wind chill (in Fahrenheit).
* Humidity(%) Shows the humidity (in percentage).
* Pressure(in) Shows the air pressure (in inches).
* Visibility(mi) Shows visibility (in miles).
* Wind_Direction Shows wind direction.
* Wind_Speed(mph) Shows wind speed (in miles per hour).
* Precipitation(in) Shows precipitation amount in inches, if there is any.
* Weather_Condition Shows the weather condition (rain, snow, thunderstorm, fog, etc.)
* Amenity A POI annotation which indicates presence of an [amenity](https://wiki.openstreetmap.org/wiki/Key:amenity) in a nearby location.
* Bump A POI annotation which indicates presence of speed bump or hump in a nearby location.
* Crossing A POI annotation which indicates presence of a pedestrian [crossing](https://wiki.openstreetmap.org/wiki/Key:crossing) in a nearby location.
* Give_Way A POI annotation which indicates presence of [give_way](https://wiki.openstreetmap.org/wiki/Tag:highway%3Dgive_way) in a nearby location.
* Junction A POI annotation which indicates presence of [junction](https://wiki.openstreetmap.org/wiki/Key:junction) in a nearby location.
* No_Exit A POI annotation which indicates presence of no exit at the end of a highway in a nearby location.
* Railway A POI annotation which indicates presence of railway in a nearby location.
* Roundabout A POI annotation which indicates presence of [roundabout](https://wiki.openstreetmap.org/wiki/Tag:junction%3Droundabout) in a nearby location.
* Station A POI annotation which indicates presence of a transit station in a nearby location.
* Stop	A POI annotation which indicates presence of stop in a nearby location.
* Traffic_Calming A POI annotation which indicates presence of [traffic_calming](https://wiki.openstreetmap.org/wiki/Key:traffic_calming) in a nearby location.
* Traffic_Signal A POI annotation which indicates presence of [traffic_signal](https://wiki.openstreetmap.org/wiki/Tag:highway%3Dtraffic_signals) in a nearby loction.
* Turning_Loop A POI annotation which indicates presence of [turning_loop](https://wiki.openstreetmap.org/wiki/Tag:highway%3Dturning_loop) in a nearby location.
* Sunrise_Sunset Shows the period of day (i.e. day or night) based on sunrise/sunset.
* Civil_Twilight Shows the period of day (i.e. day or night) based on [civil twilight](https://en.wikipedia.org/wiki/Twilight#Civil_twilight).
* Nautical_Twilight Shows the period of day (i.e. day or night) based on [nautical twilight](https://en.wikipedia.org/wiki/Twilight#Nautical_twilight).
* Astronomical_Twilight Shows the period of day (i.e. day or night) based on [astronomical twilight](https://en.wikipedia.org/wiki/Twilight#Astronomical_twilight)
* Street_Type The type of street, such as highway or local road. Larger roads like highways may not the direction of the road (N,S,E,W) at the end of the type.

This dataset is based on the dataset generated and shared by the authors of the following paper:
Moosavi, Sobhan, Mohammad Hossein Samavatian, Srinivasan Parthasarathy, and Rajiv Ramnath. “A Countrywide Traffic Accident Dataset.”, arXiv preprint arXiv:1906.05409 (2019).