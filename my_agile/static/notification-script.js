var enable_notification = document.getElementById('enable_notification');
var disable_notification = document.getElementById('disable_notification');

enable_notification.addEventListener('click', function(e) {
	e.preventDefault();
	if(!window.Notification) {
		alert('Sorry, nofications are not supported in this browser. Please use chrome instead');
	} else {
 		Notification.requestPermission(function(permission) {
			if(permission === 'denied'){
				alert('Sorry, you will not be able to see timesheet notifications');
			} else if(permission ==='granted'){
				alert('Thank you, you are now able to see timesheet notifications');
			}
		});
	}
});

disable_notification.addEventListener('click', function(e) {
	alert('Please remove notification by clicking on URL icon in your browser');
});

$(document).ready(function() {
	var userid;
	var namespace = '/timesheet';
	var io_server = 'http://' + document.domain + ':' + location.port + namespace

	var socket = io.connect(io_server);

	socket.on('connect', function() {
		// socket.emit('status', {status: 'Welcome to your dashboard'});
		socket.send('Welcome to agileXchange');
	});

	socket.on('userid', function(msg) {
		user_id = msg.userid;
	});

	socket.on('status', function(msg) {
		console.log("new notification with title = " + msg.status);
		notify = new Notification('agileXchange info', {
			body: msg.status,
			icon: 'static/tree-icon.png',
		});

	});

	socket.on('task_notification', function(msg) {
		console.log("new notification with title = " + msg.title);
		notify = new Notification(msg.title, {
			body: '['+msg.time+'] ' + msg.data,
			icon: 'static/tree-icon.png',
			tag: msg.url
		});

		notify.onclick = function() {
			notify.close();
			window.open(this.tag);
		}
	});
});

