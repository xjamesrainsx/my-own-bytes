from dotenv import dotenv_values


def test_app_config_imports_from_dotenv(server_app, plaidrunner_app):
        # Filter .env entries matching the specific mode prefix    
        mode_env_keys = {
            k: v for k, v in dotenv_values().items()
            if k.startswith("TEST_")
        }

        assert len(mode_env_keys) > 0

        # Verify each environment variable was 
        # properly set in app.config

        for env_key, expected_val in mode_env_keys.items():

            config_key = env_key[len("TEST_"):]

            assert config_key in server_app.config, f"Expected key '{config_key}' missing from app.config"
            assert config_key in plaidrunner_app.config, f"Expected key '{config_key}' missing from app.config"

            # Compare actual value against parsed dotenv value directly
            assert server_app.config[config_key] == expected_val
            assert plaidrunner_app.config[config_key] == expected_val