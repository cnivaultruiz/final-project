SELECT 
peak_name,
peak_id,
count(distinct member_id) as nb_climber,
sum(died) as nb_died,
sum(died) / count(distinct member_id) *100 as died_rate,
sum(success) as nb_success,
sum(success) / count(distinct member_id) *100 as success_rate
FROM himalaya.members
GROUP BY peak_name, peak_id
order by died_rate desc