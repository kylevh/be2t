import groovy.json.JsonOutput
import com.eviware.soapui.support.UISupport

// Define the output folder for snapshots
def outputFolder = new File(context.testCase.testSuite.project.path).getParentFile()
outputFolder = new File(outputFolder, 'snapshots')

// Create a folder for today's date
def dateFolder = new File(outputFolder, new Date().format('yyyy-MM-dd', TimeZone.getTimeZone('UTC')))
initializeFolder(dateFolder, false)

// Main function to process projects
def main(outputFolder) {
    try {
        processProjects(outputFolder)
    } catch (Exception e) {
        log.error("Failed to process projects: ${e.message}")
        log.error(e.stackTrace.join("\n"))
        throw e
    }
}

// Initialize a folder, optionally clearing it if it exists
def initializeFolder(File folder, Boolean clear = false) {
    if (folder.exists()) {
        if (clear) {
            folder.eachFile { file ->
                if (file.isDirectory()) {
                    clearFolder(file)
                }
                file.delete()
            }
            log.info("Cleared folder: ${folder.getName()}")
        }
    } else {
        folder.mkdirs()
        log.info("Created folder: ${folder.getName()}")
    }
}

// Process all projects except the current one
def processProjects(outputFolder) {
    def allProjects = com.eviware.soapui.SoapUI.getWorkspace().getProjectList()
    def currentProjectName = context.testCase.testSuite.project.name

    allProjects.findAll { project ->
        project.name != currentProjectName
    }.each { project ->
        def projectData = createProjectData(project)

        // Create output file structure
        def timestamp = new Date().format('yyyy-MM-dd_HH-mm-ss', TimeZone.getTimeZone('UTC'))
        def jsonOutput = JsonOutput.prettyPrint(JsonOutput.toJson(projectData))
        writeOutputFile(outputFolder, project, timestamp, jsonOutput)
    }
}

// Create a data structure for a project
def createProjectData(project) {
    def projectData = [
        projectName: project.name,
        testSuites: [],
        totalTestSuites: 0,
        totalTestCases: 0,
        totalPassedCases: 0,
        totalFailedCases: 0,
        totalAssertions: 0,
        totalTestSteps: 0,
        totalPassedSteps: 0,
        totalFailedSteps: 0,
    ]

    project.getTestSuiteList().each { testSuite ->
        def suiteData = createTestSuiteData(testSuite, projectData)
        projectData.totalTestSuites++
        projectData.testSuites << suiteData
    }

    return projectData
}

// Create a data structure for a test suite
def createTestSuiteData(testSuite, projectData) {
    def suiteData = [
        testSuiteName: testSuite.name,
        disabled: testSuite.isDisabled(),
        status: 'passed',
        testCases: []
    ]

    testSuite.getTestCaseList().each { testCase ->
        def testCaseData = createTestCaseData(testCase, projectData, suiteData)
        projectData.totalTestCases++
        suiteData.testCases << testCaseData
    }

    return suiteData
}

// Create a data structure for a test case
def createTestCaseData(testCase, projectData, suiteData) {
    def testCaseData = [
        testCaseName: testCase.name,
        disabled: testCase.isDisabled() || suiteData.disabled || projectData.disabled,
        status: 'passed',
        testSteps: [],
    ]

    testCase.getTestStepList().each { testStep ->
        def stepData = createTestStepData(testStep, projectData, suiteData, testCaseData)
        projectData.totalTestSteps++
        testCaseData.testSteps << stepData
    }

    return testCaseData
}

// Create a data structure for a test step
def createTestStepData(testStep, projectData, suiteData, testCaseData) {
    def stepData = [
        testStepName: testStep.getName(),
        disabled: testStep.isDisabled() || testCaseData.disabled || suiteData.disabled || projectData.disabled,
        method: null,
        endpoint: null,
        resource: null,
        pathParams: [:],
        queryParams: [:],
        headers: [:],
        requestBody: [:],
        assertions: [],
        statusCode: 'passed',
        message: null,
    ]

    if (testStep instanceof com.eviware.soapui.impl.wsdl.teststeps.RestTestRequestStep) {
        if (!stepData.disabled) {
            def result = testStep.run(testRunner, context)
            stepData.statusCode = result.getStatus().toString()
            stepData.message = result.getMessages().toString()
        }
        stepData.method = testStep.getHttpRequest().method.toString()
        stepData.resource = testStep.getResourcePath()
        stepData.endpoint = testStep.getHttpRequest().getEndpoint()
        stepData.pathParams = testStep.getRestMethod().getParams().getPropertyNames().collectEntries { name ->
            [(name): testStep.getRestMethod().getPropertyValue(name)]
        }
        stepData.headers = testStep.getHttpRequest().getRequestHeaders()
        stepData.requestBody = testStep.getHttpRequest().getRequestContent()

        testStep.getAssertionList().collect { assertion ->
            def assertionData = createAssertionsData(assertion, stepData, projectData, suiteData, testCaseData)
            projectData.totalAssertions++
            stepData.assertions << assertionData
        }
    } else {
        log.error("Unsupported test step type: ${testStep.getClass().getName()}")
        return null
    }

    return stepData
}

// Create a data structure for an assertion
def createAssertionsData(assertion, stepData, projectData, suiteData, testCaseData) {
    def assertionData = [
        type: assertion.getLabel(),
        status: assertion.status.toString()
    ]

    if (assertion.status.toString() != 'VALID') {
        stepData.statusCode = 'failed'
        testCaseData.status = 'failed'
        suiteData.status = 'failed'
        projectData.status = 'failed'
        
        // projectData.totalFailedCases++
        // projectData.totalFailedSteps++
    } else {
        // projectData.totalPassedCases++
        // projectData.totalPassedSteps++
    }

    return assertionData
}

// Write the JSON output to a file
def writeOutputFile(outputFolder, project, timestamp, jsonOutput) {
    def dateFolder = new File(outputFolder, new Date().format('yyyy-MM-dd', TimeZone.getTimeZone('UTC')))
    dateFolder.mkdirs()

    def projectFolder = new File(dateFolder, project.name)
    projectFolder.mkdirs()

    def outputFilePath = "${projectFolder}/${timestamp}.json"
    new File(outputFilePath).text = jsonOutput
    log.info("JSON export written to: ${outputFilePath}")
}

// Start the main process
main(outputFolder)

UISupport.showInfoMessage("Snapshot(s) generated with no errors")