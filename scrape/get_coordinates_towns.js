/**
 * 
Cities and Towns in Russia
==========================

Script to scrape Wikipedia for the location of around 1100 towns and cities in Russia.  
The original data is from the Russian 2010 Census.

This script runs from the command line, and requires PhantomJS and CasperJS.  
The following command runs it:

    casperjs get_coordinates_towns.js

It produces a file called `cities.json`

- - -

Install instructions of dependencies
------------------------------------

This program requires PhantomJS <http://phantomjs.org/download.html> and
CasperJS <http://casperjs.org/>. We use a recent feature of CasperJS and
we thus need at least version 1.1-beta1.

On OS X with homebrew:

    brew install phantomjs
    brew install casperjs --devel

On Linux, the easiest way to install these programs is probably to download
the binaries, unzip them in a folder called ‘src’, and create symbolic
links to their executables from a location your terminal can find.

The last step might go something like this:

    mkdir -p ~/bin/
    cd ~/bin/
    ln -s ~/src/phantomjs-1.9.1-linux-i686/bin/phantomjs
    ln -s ~/src/n1k0-casperjs-cd1fab5/bin/casperjs
    source ~/.profile

( The names of the folders depend on the specific version you download )

 * 
 */

var fs = require('fs');

var casper = require('casper').create({
    verbose: true,
    logLevel: "debug"
});

try {
    var cities = JSON.parse(fs.read('cities.json'));
}
catch (e) {
    // The file is not yet generated;
    var cities = [];
}
var cityCounter = 0;

casper.start();

casper.thenOpen ('http://en.wikipedia.org/wiki/List_of_cities_and_towns_in_Russia', function () {
    cities = this.evaluate( function() {
        function row2hash(el) {
            city = {};
            city.name_en = el.querySelector("td").textContent;
            city.href_en = 'http://en.wikipedia.org' + el.querySelector("td a").getAttribute("href");
            city.name_ru = el.querySelectorAll("td")[1].textContent;
            return city;
        }
        
        var elements = document.querySelectorAll("table.wikitable tr");
        var foundCities = [];
        
        for (var i = 0; i < elements.length; i++) {
            if (i == 0) {
                continue;
            }
            foundCities.push(row2hash(elements[i]));
        }
        
        return foundCities;
    });
});

casper.eachThen (cities, function (city) {
    var city = city.data;
    
    this.thenOpen (city.href_en, function() {
        var foundCity = this.evaluate( function () {
            var coordinates = document.querySelector(".geo").textContent.split(";").map(Number);
            return { latitude: coordinates[0], longitude: coordinates[1]};
        } );
        
        if(!foundCity || !foundCity.latitude || !foundCity.longitude) {
            this.echo('error @ ' + city.href_en);
        } else {
            cities[cityCounter].lat = foundCity.latitude;
            cities[cityCounter].lon = foundCity.longitude;
        }
        
        cityCounter += 1;
        
        fs.write("cities.json", JSON.stringify(cities, null, 2), 'w');
    });

});

casper.run(function(){ 
    this.exit();
});

