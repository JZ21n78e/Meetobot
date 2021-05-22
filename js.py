from backports import configparser
import random
class jsloader():
    def __init__(self,alias,greeting,minthreshold_value):
        # self.Xpath_joinnow = "/html/body/div[1]/c-wiz/div/div/div[8]/div[3]/div/div/div[2]/div/div[1]/div[2]/div/div[2]/div/div[1]/div[1]"
        # self.Xpath_leavenow = "/html/body/div[1]/c-wiz/div[1]/div/div[8]/div[3]/div[9]/div[2]/div[2]/div"
        # self.Xpath_mic = "/html/body/div[1]/c-wiz/div/div/div[8]/div[3]/div/div/div[2]/div/div[1]/div[1]/div[1]/div/div[4]/div[1]/div/div/div"
        # self.Xpath_cam = "/html/body/div[1]/c-wiz/div/div/div[8]/div[3]/div/div/div[2]/div/div[1]/div[1]/div[1]/div/div[4]/div[2]/div/div"
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')

        ###
        def aliasFormatter(alias):
            arr=[]
            for a in alias.split(','):
                arr.append('"'+a+'"')
            return ",".join(arr)

        self.alias = alias
        self.minthreshold_value = minthreshold_value
        # self.alias = self.config["UserConfig"]["alias"]
        self.alias_formatted = aliasFormatter(self.alias)
        self.greeting = greeting
        # self.greeting = self.config["UserConfig"]["greetings"]

        arr=self.config["UserConfig"]["messages"].split(',')
        self.message = arr[random.randint(0, len(arr)-1)]
        #custum func
        self.getElementByXpath = """
                function getElementByXpath(path) {
            return document.evaluate(path, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
            } """

        #handling chat--------
        self.joinChat = """
            document.getElementsByClassName("ZaI3hb")[1].click() """
            
        self.closeChat = """
            document.getElementsByClassName("VfPpkd-Bz112c-LgbsSe yHy1rc eT1oJ IWtuld wBYOYb")[0].click() """

        self.greet = """
        function sendText(yourtext) {
            inputElement = document.getElementsByClassName("Pc9Gce Wic03c")[0].firstChild;
            buttonElement = document.getElementsByClassName("BC4V9b")[0].children[1].firstChild;

            inputElement.value = yourtext;
            inputElement.dispatchEvent(new Event('input', {
                view: window,
                bubbles: true,
                cancelable: true
            }))
            buttonElement.click();
            }
        var greetingMessage = "%s"
        sendText(greetingMessage)
        """%(self.greeting)

        self.autoChat_captions ="""
            var autoChat_captions = setInterval(function(){
            console.log("Debug interval autoChat_captions running");
            function contains(target, pattern){
                var value = 0;
                pattern.forEach(function(word){
                value = value + target.includes(word);
                });
                return (value === 1)
            }
            function sendText(yourtext) {
            inputElement = document.getElementsByClassName("Pc9Gce Wic03c")[0].firstChild;
            buttonElement = document.getElementsByClassName("BC4V9b")[0].children[1].firstChild;

            inputElement.value = yourtext;
            inputElement.dispatchEvent(new Event('input', {
                view: window,
                bubbles: true,
                cancelable: true
            }))
            buttonElement.click();
            }
            try {
            var caps = document.getElementsByClassName("Mz6pEf wY1pdd")[0].innerText
            } catch (error) {
            console.log("error found")
            var caps = ""
            }finally{
            var arr = [%s]
            var replyMessage = '%s';
            console.log(arr,replyMessage)
            var messages = document.getElementsByClassName("z38b6 CnDs7d hPqowe")[0].innerText
            var containsName = contains(caps,arr);
            var containsReply = messages.includes(replyMessage);
            if (containsName & !containsReply ) {
                console.log(messages);
                console.log('Debug: inside captions name called -> replying');
                sendText(replyMessage);
            }
            }

            }, 2000);
            """%(self.alias_formatted,self.message)
            #
        self.autoChat = """
            var autoChat = setInterval(function(){
            console.log("Debug interval autochat running");
            function contains(target, pattern){
                var value = 0;
                pattern.forEach(function(word){
                value = value + target.includes(word);
                });
                return (value === 1)
            }
            function sendText(yourtext) {
            inputElement = document.getElementsByClassName("Pc9Gce Wic03c")[0].firstChild;
            buttonElement = document.getElementsByClassName("BC4V9b")[0].children[1].firstChild;

            inputElement.value = yourtext;
            inputElement.dispatchEvent(new Event('input', {
                view: window,
                bubbles: true,
                cancelable: true
            }))
            buttonElement.click();
            }
            
            var messages = document.getElementsByClassName("z38b6 CnDs7d hPqowe")[0].innerText
            var arr = [%s]
            var replyMessage = '%s';
            var containsName = contains(messages,arr);
            var containsReply = messages.includes(replyMessage);
            if (containsName  & !containsReply) {
            console.log(messages);
            console.log('Debug: name called -> replying');
            sendText(replyMessage);
            }
            }, 2000);
            """%(self.alias_formatted,self.message)

        #handling mic -----------
        self.muteMic = """
            var mic = document.getElementsByClassName("sUZ4id")[0].firstChild;
            console.log("mic status is --> "+ mic.dataset.isMuted);
            if (mic.dataset.isMuted=='false'){ mic.click()} 
            """
        #handling cam -----------
        self.muteCam = """
            var cam = document.getElementsByClassName("sUZ4id")[1].firstChild;
            console.log("cam status is --> "+ cam.dataset.isMuted);
            if (cam.dataset.isMuted=='false'){ cam.click()} 
            """
        
        #handling connection-------------
        self.contains = """
            function contains(selector, text) {
            var elements = document.querySelectorAll(selector);
            return Array.prototype.filter.call(elements, function(element){
                return RegExp(text).test(element.textContent);
            });
            }
            """

        self.joinnow = """{}
            contains("span","Join now")[0].click()
            """.format(self.contains)

        self.leavenow = """
            document.getElementsByClassName("s1GInc zCbbgf")[0].firstChild.firstChild.click()
            clearInterval(minth)
            clearInterval(autoChat)
            clearInterval(autoChat_captions)
            """
        self.minthresholdFunc = """
            var minth = setInterval(function(){
            var pplJoinATM = document.getElementsByClassName("rua5Nb")[0].innerText.slice(1,-1);
            var minthreshold = %s;

            console.log(pplJoinATM,minthreshold)
            if (pplJoinATM < minthreshold) {
                console.log("ppl are less then threshold , leaving call !")
                %s

            }

            }, 2000);
            """%(self.minthreshold_value,self.leavenow)

if __name__ == "__main__":
    jsloader=jsloader("Aditya , Adi, adu","yes i am here, interent issue , wifi sux",30)
    print(jsloader.alias_formatted,jsloader.message)
