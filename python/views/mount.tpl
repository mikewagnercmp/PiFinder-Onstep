% include("header.tpl", title="Mount Control Configuration")

<style>
.input-field {
  margin-bottom: 20px;
}
.input-field label {
  margin-top: 10px;
}
.helper-text {
  margin-top: 5px;
}
</style>

<div class="row valign-wrapper" style="margin: 0px;">
  <div class="col s12">
    <h5 class="grey-text">Mount Control Configuration</h5>
  </div>
</div>

<div class="card grey darken-2">
  <div class="card-content">
    % if defined('success_message'):
    <div class="row">
        <div class="col s12">
            <span class="green-text">{{ success_message }}</span>
        </div>
    </div>
    % end
    
    % if defined('error_message'):
    <div class="row">
        <div class="col s12">
            <span class="red-text">{{ error_message }}</span>
        </div>
    </div>
    % end

    <form method="post" action="/mount/update">
      <div class="row">
        <div class="input-field col s12">
          <select id="mount_type" name="mount_type">
            <option value="astro_physics" {{ 'selected' if mount_config.get('mount_type') == 'astro_physics' else '' }}>Astro Physics</option>
            <option value="onstep" {{ 'selected' if mount_config.get('mount_type') == 'onstep' else '' }}>OnStep</option>
          </select>
          <label for="mount_type">Mount Type</label>
        </div>
      </div>
      
      <div class="row">
        <div class="input-field col s12">
          <input type="text" id="host" name="host" 
                 value="{{ mount_config.get('host', '192.168.1.100') }}" 
                 placeholder="192.168.1.100" required>
          <label for="host">Mount IP Address</label>
          <span class="helper-text">Enter the IP address of your mount</span>
        </div>
      </div>
      
      <div class="row">
        <div class="input-field col s12">
          <input type="number" id="port" name="port" 
                 value="{{ mount_config.get('port', 23) }}" 
                 min="1" max="65535" required>
          <label for="port">Port</label>
          <span class="helper-text">Default: 23 for Astro Physics, 9996-9999 for OnStep</span>
        </div>
      </div>
      
      <div class="row">
        <div class="input-field col s12">
          <label>
            <input type="checkbox" id="auto_sync_enabled" name="auto_sync_enabled" 
                   {{ 'checked' if mount_config.get('auto_sync_enabled', True) else '' }}>
            <span>Enable Automatic Sync</span>
          </label>
          <span class="helper-text">Automatically sync mount when position error exceeds threshold</span>
        </div>
      </div>
      
      <div class="row">
        <div class="input-field col s12">
          <input type="number" id="sync_threshold" name="sync_threshold" 
                 value="{{ mount_config.get('sync_threshold_arcmin', 2.0) }}" 
                 min="0.1" max="10.0" step="0.1" required>
          <label for="sync_threshold">Sync Threshold (arcminutes)</label>
          <span class="helper-text">Position error threshold for automatic sync (0.1 - 10.0)</span>
        </div>
      </div>
      
      <div class="row">
        <div class="input-field col s12">
          <input type="number" id="sync_cooldown" name="sync_cooldown" 
                 value="{{ mount_config.get('sync_cooldown_minutes', 5) }}" 
                 min="0" max="60" required>
          <label for="sync_cooldown">Sync Cooldown (minutes)</label>
          <span class="helper-text">Minimum time between syncs (0 - 60)</span>
        </div>
      </div>
      
      <div class="row">
        <div class="input-field col s12">
          <input type="number" id="slew_timeout" name="slew_timeout" 
                 value="{{ mount_config.get('slew_timeout_minutes', 10) }}" 
                 min="1" max="60" required>
          <label for="slew_timeout">Slew Timeout (minutes)</label>
          <span class="helper-text">Maximum time for slew completion (1 - 60)</span>
        </div>
      </div>
      
      <div class="row">
        <div class="input-field col s12">
          <input type="number" id="slew_completion_threshold" name="slew_completion_threshold" 
                 value="{{ mount_config.get('slew_completion_threshold_arcmin', 1.0) }}" 
                 min="0.1" max="5.0" step="0.1" required>
          <label for="slew_completion_threshold">Slew Completion Threshold (arcminutes)</label>
          <span class="helper-text">Position accuracy for slew completion (0.1 - 5.0)</span>
        </div>
      </div>
      
      <div class="row">
        <div class="col s12">
          <button type="submit" class="waves-effect waves-light btn">
            <i class="material-icons left">save</i>Save Configuration
          </button>
          <a href="/" class="waves-effect waves-light btn grey">
            <i class="material-icons left">arrow_back</i>Back to Home
          </a>
        </div>
      </div>
    </form>
  </div>
</div>

<div class="card grey darken-2">
  <div class="card-content">
    <h6 class="grey-text">Test Connection</h6>
    <p>After saving your settings, you can test the mount connection from the PiFinder UI:</p>
    <ol>
      <li>Navigate to <strong>Tools → Mount Sync</strong> on your PiFinder</li>
      <li>Check the connection status</li>
      <li>Use the test functions to verify communication</li>
    </ol>
    
    <div class="card-panel blue darken-2">
      <span class="white-text">
        <strong>Note:</strong> Make sure your mount is powered on and connected to the same network as your PiFinder.
      </span>
    </div>
  </div>
</div>

<div class="card grey darken-2">
  <div class="card-content">
    <h6 class="grey-text">Mount Control Features</h6>
    <div class="row">
      <div class="col s12 m6">
        <h6 class="grey-text">Automatic Features</h6>
        <ul>
          <li><strong>Position Monitoring:</strong> Continuous tracking of mount position</li>
          <li><strong>Smart Syncing:</strong> Automatic sync when position drifts</li>
          <li><strong>Slew Management:</strong> Automatic slew completion detection</li>
          <li><strong>Error Handling:</strong> Robust error recovery and reporting</li>
        </ul>
      </div>
      <div class="col s12 m6">
        <h6 class="grey-text">Manual Controls</h6>
        <ul>
          <li><strong>Slew to Target:</strong> Command mount to specific coordinates</li>
          <li><strong>Manual Sync:</strong> Sync to current plate solve position</li>
          <li><strong>Status Monitoring:</strong> Real-time mount status display</li>
          <li><strong>Park/Unpark:</strong> Mount parking controls</li>
        </ul>
      </div>
    </div>
  </div>
</div>

<script>
  document.addEventListener('DOMContentLoaded', function() {
    var elems = document.querySelectorAll('select');
    var instances = M.FormSelect.init(elems);
  });
</script>
