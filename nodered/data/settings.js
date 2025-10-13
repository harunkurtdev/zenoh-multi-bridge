/*
 * This is a customized settings file for the SDV Node-RED example.
 */

module.exports = {
    editorTheme: {
        functionExternalModules: true,
        theme: "midnight-red",
        palette: {
            categories: ['subflows', 'common', 'function', 'network', 'sequence', 'parser', 'storage'],
        },
        projects: {
            enabled: true,
            workflow: {
                mode: "manual"
            }
        }
    }
}
