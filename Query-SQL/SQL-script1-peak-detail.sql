SELECT 
p.peak_name,
p.peak_id,
p.height_metres,
p.peak_alternative_name,
p.first_ascent_year,
p.first_ascent_country,
sum(m.died) as nb_died,
sum(m.success) as nb_success,
sum(m.success)/count(m.success) *100 as tx_success,
sum(m.oxygen_used)/count(m.oxygen_used) *100 as tx_oxygen_used,
avg(age) as age_mean
FROM peaks p
LEFT JOIN members m on p.peak_id = m.peak_id
WHERE p.peak_id = "HIUP"
GROUP BY p.peak_name, p.peak_id, p.height_metres, p.peak_alternative_name, p.first_ascent_year, p.first_ascent_country
ORDER BY peak_id 
