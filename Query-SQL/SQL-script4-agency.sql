Drop view himalaya.agency;
Create view agency as
WITH climber as (
SELECT 
expedition_id,
count(distinct member_id) as nb_climber
FROM himalaya.members
WHERE hired = 0
GROUP BY expedition_id
),
staff as (
SELECT 
expedition_id,
count(distinct member_id) as nb_staff
FROM himalaya.members
WHERE hired = 1
GROUP BY expedition_id
)
SELECT 
harmonized_agency_name,
count(distinct xp.expedition_id) as nb_expe,
count(distinct m.member_id) as nb_climber,
ROUND(sum(m.died) / count(distinct m.member_id) *100 ,2) as death_rate,
ROUND(sum(m.injured) / count(distinct m.member_id)*100 ,2) as injury_rate,
ROUND(sum(m.oxygen_used) / count(distinct m.member_id)*100 ,2) as 02_rate,
ROUND(AVG (c.nb_climber)) as avg_climber,
ROUND(AVG (s.nb_staff)) as avg_staff,
ROUND(AVG (c.nb_climber) / AVG (s.nb_staff)) as avg_staff_per_climber
FROM himalaya.expedition xp
LEFT JOIN himalaya.members m on xp.expedition_id = m.expedition_id
LEFT JOIN climber c ON c.expedition_id = xp.expedition_id
LEFT JOIN staff s ON s.expedition_id = xp.expedition_id
Group by harmonized_agency_name
order by nb_expe desc