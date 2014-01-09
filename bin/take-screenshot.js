var args = require('system').args;

if (args.length != 3) {
	console.error('Please provide two parameters: source URL and destination file name');
	phantom.exit(1);
}

var page = require('webpage').create();

page.viewportSize = {height: 768, width: 1024}

page.open(args[1], function() {
	page.render(args[2]);
	phantom.exit();
});
