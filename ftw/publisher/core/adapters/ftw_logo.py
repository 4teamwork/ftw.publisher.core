
def trigger_modified(obj, event):
    from ftw.logo.manual_override import overrides_changed
    overrides_changed(obj, event)
