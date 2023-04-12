extends CharacterBody2D


const MOVE_SPEED = 80.0
const TURN_SPEED = 5.0

#ray scanning
const FOV = 30 #degrees to either side
const N_RAYS = 100
const RAY_RANGE = 160
const BACKUP_RANGE = 60 #if something is this close, the robot backs up
#static rotation behavior
var time_rotating = 0 #dt remaining until it returns to nav

var raycasts = [] #stores last measured distance, for drawing
var vel = Vector2.ZERO
var rot = 0

#random modulation
const N_RANDS = 2
var rands = []
var d_rands = [] #derivs
var rand_min = 0.7
var rand_max = 1.0

func _init():
	#initialize raycasts array
	for i in range(N_RAYS):
		raycasts.append(0)
	for i in range(N_RANDS):
		rands.append(0.5)
		d_rands.append(0)

func argmax(xs):
	var arg = 0
	var valmax = xs[0]
	for i in range(len(xs)):
		var val = xs[i]
		if(val > valmax):
			arg = i
			valmax = val
	return arg

func get_modulation(i):
#	return 1
	var j = lerp(0, N_RANDS - 1, float(i) / (N_RAYS - 1))
	return lerp(rands[floor(j)], rands[ceil(j)], fposmod(j, 1))
	
func behavior_nav(delta):
	var rng = RandomNumberGenerator.new()
	#update random modulation
	for i in range(N_RANDS):
		d_rands[i] = (d_rands[i] + rng.randf_range(-0.1, 0.1)) * 0.99
		rands[i] = clamp(rands[i] + d_rands[i] * delta, rand_min, rand_max)
	#reset velocity to zero
	velocity = Vector2.ZERO
	#raycasts
	#also calculate overall movement direction
	var movement_direction = Vector2.ZERO
	for i in range(N_RAYS):
		#cast ray
		var angle = deg_to_rad(lerp(-FOV, FOV, float(i) / (N_RAYS - 1)))
		var ray = Vector2(cos(angle), sin(angle)) * RAY_RANGE
		var raycaster:RayCast2D = $RayCast
		raycaster.target_position = ray
		raycaster.force_raycast_update()
		var hit_dist = RAY_RANGE
		if(raycaster.is_colliding()):
			hit_dist = to_local(raycaster.get_collision_point()).length()
		raycasts[i] = hit_dist
		#add to overall direction
		#weighted by cos of angle and some randomness
		var length = hit_dist * get_modulation(i) - BACKUP_RANGE
		if(length > 0):
			length = length / (RAY_RANGE - BACKUP_RANGE)
		else:
			length = length / BACKUP_RANGE
		ray = ray.normalized() * length * cos(angle)
#		#
		movement_direction += ray
	#
	movement_direction = movement_direction / N_RAYS
	if(movement_direction.length() < 0.1):
		var rand_rot = rng.randf_range(-PI, PI)
		time_rotating += rand_rot / TURN_SPEED
	#
	movement_direction = movement_direction.normalized()

	#determine overall direction
	#(go towards max dist)
	
	#convert direction to motor commands
	
	#convert motor commands to velocity
	
	#move
	rot = atan2(movement_direction.y, movement_direction.x) * TURN_SPEED
	var rotation_rate = rot * delta
	rotate(rotation_rate)
	
	vel = Vector2(movement_direction.x * MOVE_SPEED, 0)
	var new_vel = vel.rotated(rotation)
	velocity = new_vel
	move_and_slide()

func behavior_rotate(delta):
	rot = TURN_SPEED * sign(time_rotating)
	var rotation_rate = rot * delta
	rotate(rotation_rate)
	#
	if(time_rotating < 0):
		time_rotating = min(time_rotating + delta, 0)
	else:
		time_rotating = max(time_rotating - delta, 0)
	
func _physics_process(delta):
	if(time_rotating != 0):
		behavior_rotate(delta)
	else:
		behavior_nav(delta)
	
func _process(_delta):
	queue_redraw()
	
func _draw():
	if(time_rotating != 0):
		return
	for i in range(N_RAYS):
		var angle = deg_to_rad(lerp(-FOV, FOV, float(i) / (N_RAYS - 1)))
		var dist = raycasts[i]
		var ray = Vector2(cos(angle), sin(angle)) * dist
		var color = Color.BLUE
		if(dist < RAY_RANGE):
			if(dist > BACKUP_RANGE):
				color = lerp(Color.YELLOW, Color.GREEN, (dist - BACKUP_RANGE) / (RAY_RANGE - BACKUP_RANGE))
			else:
				color = Color.RED
		draw_line(Vector2.ZERO, ray, color, -1.0, true)
	#draw current random modulation
	var draw_min = 20
	var draw_max = 40
	for i in range(N_RAYS - 1):
		var rand1 = lerp(draw_min, draw_max, get_modulation(i))
		var angle1 = deg_to_rad(lerp(-FOV, FOV, float(i) / (N_RAYS - 1)))
		var vec1 = Vector2(cos(angle1), sin(angle1)) * rand1
		var rand2 = lerp(draw_min, draw_max, get_modulation(i + 1))
		var angle2 = deg_to_rad(lerp(-FOV, FOV, float(i + 1) / (N_RAYS - 1)))
		var vec2 = Vector2(cos(angle2), sin(angle2)) * rand2
		draw_line(vec1, vec2, Color.PURPLE, -1.0, true)
	#
	for i in range(N_RAYS - 1):
		var d1 = lerp(draw_min, draw_max, rand_min)
		var angle1 = deg_to_rad(lerp(-FOV, FOV, float(i) / (N_RAYS - 1)))
		var vec1 = Vector2(cos(angle1), sin(angle1)) * d1
		var d2 = lerp(draw_min, draw_max, rand_min)
		var angle2 = deg_to_rad(lerp(-FOV, FOV, float(i + 1) / (N_RAYS - 1)))
		var vec2 = Vector2(cos(angle2), sin(angle2)) * d2
		#inner
		draw_line(vec1, vec2, Color.BLACK, -1.0, true)
		#outer
		vec1 = vec1.normalized() * lerp(draw_min, draw_max, rand_max)
		vec2 = vec2.normalized() * lerp(draw_min, draw_max, rand_max)
		draw_line(vec1, vec2, Color.BLACK, -1.0, true)
	#draw velocity
	draw_line(Vector2.ZERO, vel.rotated(rot), Color.BLACK, -1.0, true)
