MAIN_QUERY = """--sql 
EXECUTE IMMEDIATE FORMAT(
    --commas
      SELECT * EXCEPT(product_property_id, extracted_from, level_property_id, level_name) FROM
    (
  SELECT DISTINCT
  product_property_id, 
  pp.master_product_id, 
  prod.product_name,
  prod.product_image_url,
 --property_id,
  mp.property_name,
  pp.master_category_id, 
  cat.category_name,
  cat.subcategory_name,
  pp.level_property_id, 
  level_name, 
  extracted_from,
  value_string AS value, 
  FROM `prod-shelftia-as.master_catalogs.product_properties`  As pp 
  INNER JOIN `master_catalogs.master_properties` AS mp
  ON mp.property_id = pp.property_id
  INNER JOIN `master_catalogs.master_products` AS prod 
  ON pp.master_product_id = prod.master_product_id
  INNER JOIN `master_catalogs.master_categories` AS cat 
  ON pp.master_category_id = cat.master_category_id
  WHERE value_string IS NOT NULL
  UNION ALL 
  SELECT DISTINCT
  product_property_id, 
  pp.master_product_id, 
  prod.product_name,
  prod.product_image_url,
 --property_id,
  mp.property_name,
  pp.master_category_id, 
  cat.category_name,
  cat.subcategory_name,
  pp.level_property_id, 
  level_name, 
  extracted_from,
  CAST(value_numeric AS STRING) AS value, 
  FROM `prod-shelftia-as.master_catalogs.product_properties`  As pp 
  INNER JOIN `master_catalogs.master_properties` AS mp
  ON mp.property_id = pp.property_id
  INNER JOIN `master_catalogs.master_products` AS prod 
  ON pp.master_product_id = prod.master_product_id
  INNER JOIN `master_catalogs.master_categories` AS cat 
  ON pp.master_category_id = cat.master_category_id
  WHERE value_numeric IS NOT NULL
  UNION ALL
--   SELECT DISTINCT
--   product_property_id, 
--   pp.master_product_id, 
--   prod.product_name,
--  --property_id,
--   mp.property_name,
--   pp.master_category_id, 
--   cat.subcategory_name,
--   pp.level_property_id, 
--   level_name, 
--   extracted_from,
--   value_list, 
--   FROM `prod-shelftia-as.master_catalogs.product_properties`  As pp 
--   INNER JOIN `master_catalogs.master_properties` AS mp
--   ON mp.property_id = pp.property_id
--   INNER JOIN `master_catalogs.master_products` AS prod 
--   ON pp.master_product_id = prod.master_product_id
--   INNER JOIN `master_catalogs.master_categories` AS cat 
--   ON pp.master_category_id = cat.master_category_id
--   UNION ALL 
  SELECT DISTINCT
  product_property_id, 
  pp.master_product_id, 
  prod.product_name,
  prod.product_image_url,
 --property_id,
  mp.property_name,
  pp.master_category_id, 
  cat.category_name,
  cat.subcategory_name,
  pp.level_property_id, 
  level_name, 
  extracted_from,
  CASE WHEN value_bool THEN 'TRUE' ELSE 'FALSE' END AS value,
  FROM `prod-shelftia-as.master_catalogs.product_properties`  As pp 
  INNER JOIN `master_catalogs.master_properties` AS mp
  ON mp.property_id = pp.property_id
  INNER JOIN `master_catalogs.master_products` AS prod 
  ON pp.master_product_id = prod.master_product_id
  INNER JOIN `master_catalogs.master_categories` AS cat 
  ON pp.master_category_id = cat.master_category_id
  WHERE value_bool IS NOT NULL
   )
  PIVOT(STRING_AGG(value) FOR property_name IN %s)
  ;
    --commas,
    ( SELECT CONCAT("(", STRING_AGG(DISTINCT CONCAT("'", property_name, "'"), ','), ")")  FROM `master_catalogs.master_properties`
    WHERE property_id IN (
      SELECT DISTINCT property_id  FROM  `prod-shelftia-as.master_catalogs.product_properties`
      --WHERE value IS NOT NULL
    )
    )
  )
"""