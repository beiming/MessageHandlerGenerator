package com.sg.game.tr.net.message {
	import flash.utils.IDataInput;
	import com.sg.game.tr.net.handler.*;
	import com.sg.game.tr.net.data.*;
	import com.sg.game.framework.core.Long;
	import com.sg.game.framework.net.AbstractMessageReceiver;
	import com.sg.game.tr.net.MessageType;
	import com.sg.game.tr.common.data.*;
	
	public class TestGCMessage extends AbstractMessageReceiver
	{
		override protected function collectObservers():void
		{
				register(MessageType.GC_TEST,GC_TEST);
		}

 		/**
		 * test
		 * @param null
		 */
		public function GC_TEST(data:IDataInput):void
		{
			TroopsHandler.GC_FEATURE_INFO();
		}
	}
}