extends CharacterBody2D


const SPEED = 60.0
const TURN_SPEED = 8.0

#ray scanning
const FOV = 30 #degrees to either side
const N_RAYS = 100
const RAY_RANGE = 160
const BACKUP_RANGE = 60 #if something is this close, the robot backs up

var raycasts = [] #stores last measured distance
var fraction_hit = 0

#random modulation
const N_RANDS = 2
var rands = []
var d_rands = [] #derivs

var rotation_rate = 0.0

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

func get_modulation_a(i):
	var j = lerp(0, N_RANDS - 1, float(i) / (N_RAYS - 1))
	return lerp(rands[floor(j)], rands[ceil(j)], fposmod(j, 1))
	
func get_modulation_b(i):
	var part = float(i) / (N_RAYS - 1)
	var part_halved = abs(part - 0.5) * 2
	return max(part_halved * part_halved, 1 - fraction_hit)

func _physics_process(delta):
	var rng = RandomNumberGenerator.new()
	#update random modulation
	for i in range(N_RANDS):
		d_rands[i] = (d_rands[i] + rng.randf_range(-0.1, 0.1)) * 0.99
		rands[i] = clamp(rands[i] + d_rands[i] * delta, 0.8, 1.0)
	#reset velocity to zero
#	velocity = Vector2.ZERO
	#raycasts
	#also calculate overall movement direction
	var movement_direction = Vector2.ZERO
	var rays_hit = 0
	for i in range(N_RAYS):
		var angle = deg_to_rad(lerp(-FOV, FOV, float(i) / (N_RAYS - 1)))
		var ray = Vector2(cos(angle), sin(angle)) * RAY_RANGE
		var raycaster:RayCast2D = $RayCast
		raycaster.target_position = ray
		raycaster.force_raycast_update()
		var hit_dist = RAY_RANGE
		if(raycaster.is_colliding()):
			hit_dist = to_local(raycaster.get_collision_point()).length()
			rays_hit += 1
		raycasts[i] = hit_dist
		#add to overall direction
		#weighted by cos of angle and some randomness
		var length = hit_dist * get_modulation_a(i) - BACKUP_RANGE
		if(length > 0):
			length = length / (hit_dist - BACKUP_RANGE)
		else:
			length = length / BACKUP_RANGE
		movement_direction += ray.normalized() * length * cos(angle) * get_modulation_b(i)
	#
	fraction_hit = float(rays_hit) / N_RAYS
#	movement_direction = lerp(movement_direction, -movement_direction, fraction_hit * fraction_hit)
	#
	movement_direction = movement_direction.normalized()
	#modulate distances by randomness over time
	#determine overall direction
	#(go towards max dist)
	
	#convert direction to motor commands
	
	#convert motor commands to velocity
	
	#move
	var new_rotation_rate = atan2(movement_direction.y, movement_direction.x) * delta * TURN_SPEED
	rotation_rate = lerp(rotation_rate, new_rotation_rate, 0.03) #smoothing
	rotate(rotation_rate)
	var new_vel = Vector2(movement_direction.x * SPEED / (abs(movement_direction.y) + 1), 0).rotated(rotation)
	velocity = lerp(velocity, new_vel, 0.03) #smoothing
	move_and_slide()
	
func _process(_delta):
	queue_redraw()
	
func _draw():
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
	for i in range(N_RAYS - 1):
		var rand1 = get_modulation_a(i) * 20 + 20
		var angle1 = deg_to_rad(lerp(-FOV, FOV, float(i) / (N_RAYS - 1)))
		var vec1 = Vector2(cos(angle1), sin(angle1)) * rand1
		var rand2 = get_modulation_a(i + 1) * 20 + 20
		var angle2 = deg_to_rad(lerp(-FOV, FOV, float(i + 1) / (N_RAYS - 1)))
		var vec2 = Vector2(cos(angle2), sin(angle2)) * rand2
		draw_line(vec1, vec2, Color.PURPLE, -1.0, true)
		
		rand1 = get_modulation_b(i) * 20 + 20
		angle1 = deg_to_rad(lerp(-FOV, FOV, float(i) / (N_RAYS - 1)))
		vec1 = Vector2(cos(angle1), sin(angle1)) * rand1
		rand2 = get_modulation_b(i + 1) * 20 + 20
		angle2 = deg_to_rad(lerp(-FOV, FOV, float(i + 1) / (N_RAYS - 1)))
		vec2 = Vector2(cos(angle2), sin(angle2)) * rand2
		draw_line(vec1, vec2, Color.PURPLE, -1.0, true)
		
		
		vec1 = vec1.normalized() * (20 + 20 * 0.8)
		vec2 = vec2.normalized() * (20 + 20 * 0.8)
		draw_line(vec1, vec2, Color.BLACK, -1.0, true)
		vec1 = vec1.normalized() * 40
		vec2 = vec2.normalized() * 40
		draw_line(vec1, vec2, Color.BLACK, -1.0, true)
