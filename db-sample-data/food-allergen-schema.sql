-- Food Allergen Classification data table setup.
-- Run against the dashboard data database before food-allergen-seed.sql.

CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA public;

CREATE TABLE IF NOT EXISTS public.food_allergen_classification (
    id serial PRIMARY KEY,
    county text,
    company_name text,
    brand_name text,
    product_name text,
    ingredients text,
    has_allergens boolean,
    allergens text,
    allergen_count int,
    lat double precision,
    lon double precision,
    wkb_geometry public.geometry(Point, 4326),
    data_time timestamp,
    classified_at timestamp DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_food_allergen_company
    ON public.food_allergen_classification(company_name);

CREATE INDEX IF NOT EXISTS idx_food_allergen_brand
    ON public.food_allergen_classification(brand_name);

CREATE INDEX IF NOT EXISTS idx_food_allergen_geom
    ON public.food_allergen_classification USING GIST(wkb_geometry);

CREATE OR REPLACE FUNCTION public.update_food_allergen_geometry()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.lat IS NOT NULL AND NEW.lon IS NOT NULL THEN
        NEW.wkb_geometry = public.ST_SetSRID(public.ST_MakePoint(NEW.lon, NEW.lat), 4326);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_food_allergen_geometry
    ON public.food_allergen_classification;

CREATE TRIGGER trigger_food_allergen_geometry
BEFORE INSERT OR UPDATE ON public.food_allergen_classification
FOR EACH ROW
EXECUTE FUNCTION public.update_food_allergen_geometry();
