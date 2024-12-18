import groovy.json.JsonOutput
import com.eviware.soapui.support.UISupport

// Define output folder setup
def outputFolder = new File(context.testCase.testSuite.project.path).getParentFile().getParentFile()
outputFolder = new File(outputFolder, 'snapshots')
def dateFolder = new File(outputFolder, new Date().format('yyyy-MM-dd', TimeZone.getTimeZone('America/New_York')))

// Project Snapshot Class
class ProjectSnapshot {
    static final def DEV_SUITE_PATTERNS = ['DEV', 'Dev']
    static final def SAT_SUITE_PATTERNS = ['SAT', 'Sat']
    
    def project
    def testRunner
    def context
    def data = [
        projectName: '',
        testSuites: [],
        metrics: [
            projectStatus: 'passed',
            suiteCount: 0,
            caseCount: 0,
            passedCaseCount: 0,
            failedCaseCount: 0,
            assertionCount: 0,
            stepCount: 0,
            enabledStepCount: 0,
            passedStepCount: 0,
            failedStepCount: 0,
            coveragePercentage: 0,
            devMetrics: [
                passedCaseCount: 0,
                failedCaseCount: 0,
                enabledCaseCount: 0,
                totalCaseCount: 0,
                enabledStepCount: 0,
                totalStepCount: 0,
                passedStepCount: 0,
                failedStepCount: 0,
                coveragePercentage: 0
            ],
            // Add new SAT metrics
            satMetrics: [
                passedCaseCount: 0,
                failedCaseCount: 0,
                enabledCaseCount: 0,
                totalCaseCount: 0,
                enabledStepCount: 0,
                totalStepCount: 0,
                passedStepCount: 0,
                failedStepCount: 0,
                coveragePercentage: 0
            ]
        ],
    ]

    ProjectSnapshot(project, testRunner, context) {
        this.project = project
        this.testRunner = testRunner
        this.context = context
        this.data.projectName = project.name
    }

    def collect() {
        project.testSuiteList.each { suite ->
            def suiteSnapshot = new TestSuiteSnapshot(suite, testRunner, context)
            def suiteData = suiteSnapshot.collect()
            data.testSuites << suiteData
            
            data.metrics.suiteCount++
            data.metrics.caseCount += suiteSnapshot.testCaseCount
            data.metrics.assertionCount += suiteSnapshot.assertionCount
            data.metrics.stepCount += suiteSnapshot.stepCount
            data.metrics.enabledStepCount += suiteSnapshot.enabledStepCount
            data.metrics.passedStepCount += suiteSnapshot.passedSteps
            data.metrics.failedStepCount += suiteSnapshot.failedSteps
            data.metrics.passedCaseCount += suiteSnapshot.passedCases
            data.metrics.failedCaseCount += suiteSnapshot.failedCases
            
            if (suiteData.status == 'failed') {
                data.metrics.projectStatus = 'failed'
            }
        }

        if (data.metrics.enabledStepCount > 0) {
            data.metrics.coveragePercentage = (data.metrics.passedStepCount / data.metrics.enabledStepCount * 100).round(2)
        }

        return data
    }
}

// Test Suite Snapshot Class
class TestSuiteSnapshot {
    def suite
    def testCaseCount = 0
    def assertionCount = 0
    def stepCount = 0
    def enabledStepCount = 0
    def passedSteps = 0
    def failedSteps = 0
    def passedCases = 0
    def failedCases = 0
    def testRunner
    def context

    TestSuiteSnapshot(suite, testRunner, context) {
        this.suite = suite
        this.testRunner = testRunner
        this.context = context
    }

    def collect() {
        def suiteData = [
            testSuiteName: suite.name,
            disabled: suite.disabled,
            status: 'passed',
            testCases: []
        ]

        suite.testCaseList.each { testCase ->
            def caseSnapshot = new TestCaseSnapshot(testCase, suite.disabled, testRunner, context)
            def caseData = caseSnapshot.collect()
            suiteData.testCases << caseData
            
            testCaseCount++
            assertionCount += caseSnapshot.assertionCount
            stepCount += caseSnapshot.stepCount
            enabledStepCount += caseSnapshot.enabledStepCount
            passedSteps += caseSnapshot.passedSteps
            failedSteps += caseSnapshot.failedSteps
            
            if (caseData.status == 'failed') {
                suiteData.status = 'failed'
                failedCases++
            } else {
                passedCases++
            }
        }

        return suiteData
    }
}

// Test Case Snapshot Class
class TestCaseSnapshot {
    def testCase
    def parentDisabled
    def assertionCount = 0
    def stepCount = 0
    def enabledStepCount = 0
    def passedSteps = 0
    def failedSteps = 0
    def testRunner
    def context

    TestCaseSnapshot(testCase, parentDisabled, testRunner, context) {
        this.testCase = testCase
        this.parentDisabled = parentDisabled
        this.testRunner = testRunner
        this.context = context
    }

    def collect() {
        def testCaseData = [
            testCaseName: testCase.name,
            disabled: testCase.disabled || parentDisabled,
            status: 'passed',
            testSteps: []
        ]

        testCase.testStepList.each { step ->
            def stepSnapshot = new TestStepSnapshot(step, testCaseData.disabled, testRunner, context)
            def stepData = stepSnapshot.collect()
            if (stepData) {  // Only add if step data exists
                testCaseData.testSteps << stepData
                stepCount++
                if(!stepData.disabled) {
                    enabledStepCount++
                }
                assertionCount += stepSnapshot.assertionCount
                
                if (stepData.statusCode == 'failed') {
                    testCaseData.status = 'failed'
                    failedSteps++
                } else {
                    passedSteps++
                }
            }
        }

        return testCaseData
    }
}

// Test Step Snapshot Class
class TestStepSnapshot {
    def step
    def parentDisabled
    def testRunner
    def context
    def assertionCount = 0

    TestStepSnapshot(step, parentDisabled, testRunner, context) {
        this.step = step
        this.parentDisabled = parentDisabled
        this.testRunner = testRunner
        this.context = context
    }

    def collect() {
        // Only process REST steps
        if (!(step instanceof com.eviware.soapui.impl.wsdl.teststeps.RestTestRequestStep)) {
            log.info("ERROR: Skipping step ${step.name} as it is not a REST step")
            return null
        }

        def notes = ''
        try {
            def testCase = step.testCase
            if (testCase?.properties) {
                def property = testCase.properties.get(step.name)
                notes = property?.value ?: ''
            }
        } catch (Exception e) {
            log.warn("Could not retrieve notes for step ${step.name}: ${e.message}")
        }

        def stepData = [
            testStepName: step.name,
            description: step.description ?: '',
            notes: notes,
            disabled: step.disabled || parentDisabled,
            method: step.httpRequest.method.toString(),
            endpoint: step.httpRequest.endpoint,
            resource: step.resourcePath,
            pathParams: [:],
            queryParams: [:],
            headers: [:],
            requestBody: step.httpRequest.requestContent,
            assertions: [],
            statusCode: 'passed',
            message: null
        ]

        // if (!stepData.disabled) {
        //     try {
        //         def result = step.run(testRunner, context)
        //         stepData.statusCode = result.status.toString()
        //         stepData.message = result.messages.toString()
        //     } catch (Exception e) {
        //         stepData.statusCode = 'failed'
        //         stepData.message = e.message
        //     }
        // }
        if (!stepData.disabled) {
            try {
                def result = step.run(testRunner, context)
                // Only set initial status from result if it's a failure
                if (result.status.toString() != 'OK') {
                    stepData.statusCode = result.status.toString()
                }
                stepData.message = result.messages.toString()
            } catch (Exception e) {
                stepData.statusCode = 'failed'
                stepData.message = e.message
            }
        }

        // Collect path parameters
        step.restMethod.params.propertyNames.each { name ->
            stepData.pathParams[name] = step.restMethod.getPropertyValue(name)
        }

        // Collect headers
        stepData.headers = step.httpRequest.requestHeaders

        // Process assertions
        step.assertionList.each { assertion ->
            assertionCount++
            def assertionData = [
                type: assertion.label,
                status: assertion.status.toString()
            ]
            
            if (assertion.status.toString() != 'VALID') {
                stepData.statusCode = 'failed'
            }
            
            stepData.assertions << assertionData
        }

        return stepData
    }
}

// Helper function to initialize folders
def initializeFolder(File folder, Boolean clear = false) {
    if (folder.exists()) {
        if (clear) {
            folder.eachFile { file ->
                if (file.isDirectory()) {
                    file.deleteDir()
                } else {
                    file.delete()
                }
            }
            log.info("Cleared folder: ${folder.name}")
        }
    } else {
        folder.mkdirs()
        log.info("Created folder: ${folder.name}")
    }
}

// Main processing function
def processProjects(outputFolder, dateFolder) {
    def currentProjectName = context.testCase.testSuite.project.name
    
    com.eviware.soapui.SoapUI.workspace.projectList
        .findAll { it.name != currentProjectName }
        .collectEntries { project ->
            try {
                def snapshot = new ProjectSnapshot(project, testRunner, context)
                def projectData = snapshot.collect()
                def timestamp = new Date().format('yyyy-MM-dd_HH-mm-ss', TimeZone.getTimeZone('UTC'))
                
                // Create project folder and write file in one operation
                def projectFolder = new File(dateFolder, project.name).with { mkdirs(); it }
                new File(projectFolder, "${timestamp}.json").with { 
                    text = JsonOutput.prettyPrint(JsonOutput.toJson(projectData))
                }
                
                log.info("Generated snapshot for project: ${project.name}")
                [project.name, true]
            } catch (Exception e) {
                log.error("Failed to process project ${project.name}: ${e.message}")
                log.error(e.stackTrace.join("\n"))
                [project.name, false]
            }
        }
}

// Execute
try {
    initializeFolder(dateFolder, false)
    processProjects(outputFolder, dateFolder)
    UISupport.showInfoMessage("Snapshot(s) generated successfully")
} catch (Exception e) {
    log.error("Failed to generate snapshots: ${e.message}")
    log.error(e.stackTrace.join("\n"))
    UISupport.showErrorMessage("Failed to generate snapshots: ${e.message}")
}