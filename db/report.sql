SELECT  a.project_id,b.material_id, 
sum( case when a.note_type = '入库单'  then b.quantity else 0 end) as 'inload',
sum(case when a.note_type = '出库单'  then b.quantity else 0 end) as 'outload',
sum(case when a.note_type = '退料单'  then b.quantity else 0 end) as 'return'
FROM warehousenote a  inner join warehousenoteitem b on a.id=b.note_id
 group by a.project_id,b.material_id;

  