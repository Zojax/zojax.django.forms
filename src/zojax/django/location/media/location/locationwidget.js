(function() {
	
	PRECISION_PRIORITY = [
      'street_address',
      'sublocality',	                      
      'locality',
	  'administrative_area_level_3',
	  'administrative_area_level_2',
	  'administrative_area_level_1',
	  'country',
    ];
	
	window.LocationWidget = function(canvas, lat_field, lng_field, search_field, search_button, precision) {
		this.$canvas = $(canvas);
		this.$lat_field = $(lat_field);
		this.$lng_field = $(lng_field);
		this.$search_field = $(search_field);
		this.$search_button = $(search_button);
		this.precision = precision;
		this.init();
	}
	
	LocationWidget.prototype = {
		init: function() {
			var lat = this.$lat_field.val();
			var lng = this.$lng_field.val();
			var initial_location = null;
			if (lat != '' && lng != '') {
				initial_location = new google.maps.LatLng(parseFloat(lat), parseFloat(lng));
			}
			this.geocoder = new google.maps.Geocoder();
			var map_options = {
				zoom: 8,
				mapTypeId: google.maps.MapTypeId.ROADMAP
		    };
			if (initial_location != null) {
				map_options.center = initial_location;	
			}
			this.map = new google.maps.Map(this.$canvas.get(0), map_options);
		    this.marker = new google.maps.Marker({
		        map: this.map, 
		        position: this.map.getCenter()
		    });
			if (initial_location != null) {
				this.setMarker(initial_location);
			}
		    this.info_window = new google.maps.InfoWindow();
		    var self = this;
		    google.maps.event.addListener(this.map, 'click', function(event) {
		        self.setMarker(event.latLng);
		    });
		    this.$search_button.click(function() {self.search();});
		    this.$search_field.keydown(function(event) {
		    	if (event.keyCode == '13') {
		    		self.search();
		    	    event.preventDefault();
		        }
	    	});
		},
		
		setMarker: function(location) {
			this.marker.setPosition(location);
			this.$lat_field.val(location.lat());
			this.$lng_field.val(location.lng());
			var self = this;
			this.geocoder.geocode({'latLng': location}, function(results, status) {
				var address = null;
				if (status == google.maps.GeocoderStatus.OK) {
					if (results.length) {
						for (var i = PRECISION_PRIORITY.indexOf(self.precision); i < PRECISION_PRIORITY.length; i++) {
							var precision = PRECISION_PRIORITY[i]; 
							for (var j = 0; j < results.length; j++) {
								var result = results[j];
								if (result.types.indexOf(precision) != -1) {
									address = result.formatted_address;
									break;
								}
							}
							if (address != null) {
								break;
							}
							if (address == null) {
								address = results[0].formatted_address;
							}
						}
					}
					if (address != null) {
						self.info_window.setContent(address);
						self.info_window.open(self.map, self.marker);
					} else {
						self.info_window.close();
					}
				} else {
					alert("Geocoder failed due to: " + status);
				}
			});
		},
		
		search: function() {
			var address = this.$search_field.val();
			if (address == '') {
				return;
			}
			var self = this;
			this.geocoder.geocode({'address': address}, function(results, status) {
				if (status == google.maps.GeocoderStatus.OK) {
					if (results.length) {
						self.setMarker(results[0].geometry.location);
					}
				} else {
					alert("Geocoder failed due to: " + status);
				}
			});
		}
	};
})();