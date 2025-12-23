-- ============================================================
-- AUTO-CREATE TENANT ON USER SIGNUP
-- ============================================================
-- This trigger automatically creates a tenant and user record
-- when a new auth user signs up via the dashboard
-- ============================================================

-- Function to handle new user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
DECLARE
    new_tenant_id UUID;
    company_name TEXT;
BEGIN
    -- Get company name from user metadata, default to email prefix
    company_name := COALESCE(
        NEW.raw_user_meta_data->>'company_name',
        split_part(NEW.email, '@', 1) || '''s Company'
    );

    -- Create new tenant
    INSERT INTO public.tenants (name, email)
    VALUES (company_name, NEW.email)
    RETURNING id INTO new_tenant_id;

    -- Create user record linked to tenant
    INSERT INTO public.users (id, tenant_id, email, full_name, role)
    VALUES (
        NEW.id,
        new_tenant_id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'full_name', split_part(NEW.email, '@', 1)),
        'owner'
    );

    -- Update user metadata with tenant_id for frontend access
    UPDATE auth.users
    SET raw_user_meta_data = raw_user_meta_data || jsonb_build_object('tenant_id', new_tenant_id::text)
    WHERE id = NEW.id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger on auth.users insert
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO postgres, anon, authenticated, service_role;
GRANT ALL ON public.tenants TO postgres, service_role;
GRANT ALL ON public.users TO postgres, service_role;
