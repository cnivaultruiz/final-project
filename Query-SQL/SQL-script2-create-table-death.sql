
Create table death
SELECT 
expedition_id,
member_id,
m.peak_id,
m.peak_name,
year,
season,
sex,
age,
citizenship,
hired,
highpoint_metres,
solo,
oxygen_used,
death_cause,
death_height_metres,
p.longitude,
p.latitude
FROM himalaya.members m
LEFT JOIN himalaya.peaks p ON m.peak_id = p.peak_id
WHERE died = 1