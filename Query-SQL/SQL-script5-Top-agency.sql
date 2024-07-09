SELECT 
harmonized_agency_name,
count(distinct expedition_id) as nb_expedition,
sum(is_success)/count(distinct expedition_id)  as success_rate
FROM himalaya.expedition
WHERE harmonized_agency_name != 'Unknown'
GROUP BY harmonized_agency_name
ORDER BY nb_expedition desc